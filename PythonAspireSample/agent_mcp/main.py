"""
Agent MCP Service

Minimal, typed Agent MCP (FastMCP) that manages agents and runs, and discovers MCP tools.
Agents load MCP tools dynamically and run as LangGraph apps (Plan→Act or ReAct+done).

Follows principles from Grokking Simplicity and A Philosophy of Software Design:
- Separates calculations (pure functions) from actions (I/O)
- Deep modules with simple interfaces
- Fully async for all I/O operations
- Uses DefaultAzureCredential for secure Azure authentication
"""

from __future__ import annotations

import asyncio
import ast
import contextlib
import math
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

import fastapi
import fastapi.responses
import opentelemetry.instrumentation.fastapi as otel_fastapi
import telemetry
from azure.core.exceptions import ResourceExistsError
from azure.data.tables import UpdateMode
from azure.data.tables.aio import TableServiceClient
from azure.identity.aio import DefaultAzureCredential
from pydantic import BaseModel, Field

# FastAPI app setup
@contextlib.asynccontextmanager
async def lifespan(app_instance):
    """Lifespan context manager for FastAPI app."""
    telemetry.configure_opentelemetry()
    # Seed demo agents on startup
    await seed_demo_agents()
    yield


app = fastapi.FastAPI(
    lifespan=lifespan,
    title="Agent MCP Service",
    description="Agent management and MCP tool discovery service",
)
otel_fastapi.FastAPIInstrumentor.instrument_app(app, exclude_spans=["send"])


# ------------------- Typed models (agent, mcp, run) -------------------


class LLMConfig(BaseModel):
    """Configuration for Language Model."""

    model: str
    temperature: float = 0.0
    params: Dict[str, Any] = Field(default_factory=dict)


class RunConfig(BaseModel):
    """Configuration for agent run execution."""

    max_steps: int = 8
    timeout_seconds: int = 300  # 5 minutes


class MCPServerCfg(BaseModel):
    """Configuration for MCP server connection."""

    transport: Literal["stdio", "streamable_http", "sse"] = "streamable_http"
    url: Optional[str] = None
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)


class AgentDef(BaseModel):
    """Complete agent definition with tools, LLM config, and MCP servers."""

    id: str
    partition: str = "Agents"
    system_prompt: str
    tools: List[str] = Field(default_factory=list)
    llm: LLMConfig
    input_params: Dict[str, Any] = Field(default_factory=dict)
    output_config: Dict[str, Any] = Field(default_factory=dict)
    triggers: List[Dict[str, Any]] = Field(default_factory=list)
    run: RunConfig = Field(default_factory=RunConfig)
    use_plan: bool = True
    mcp_servers: Dict[str, MCPServerCfg] = Field(default_factory=dict)


class ServerSpec(BaseModel):
    """Specification for an MCP server."""

    name: str
    transport: Literal["stdio", "streamable_http", "sse"]
    url: Optional[str] = None
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)


class ToolRef(BaseModel):
    """Reference to a tool on an MCP server."""

    server: str
    name: str
    description: str = ""


class LogEvent(BaseModel):
    """Log event from agent execution."""

    ts: str
    node: str
    text: str


class RunInfo(BaseModel):
    """Information about an agent run."""

    session_id: str
    agent_id: str
    status: Literal["running", "done", "timeout", "stopped", "error"]
    start_ts: str
    end_ts: Optional[str] = None
    log_len: int = 0


class RunLogsOut(BaseModel):
    """Output containing run logs."""

    lines: List[LogEvent]
    next_cursor: int
    done: bool


# ------------------- Pure calculations (no side effects) -------------------


def create_log_event(node: str, text: str) -> LogEvent:
    """Create a log event with timestamp. Pure calculation."""
    return LogEvent(
        ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        node=node,
        text=text,
    )


def format_log_content(content: Any) -> str:
    """Format log content to string. Pure calculation."""
    if isinstance(content, list):
        content = " ".join(
            str(p.get("text", "")) if isinstance(p, dict) else str(p) for p in content
        )
    return str(content).replace("\n", " ")[:200]


def extract_server_specs(agent: AgentDef) -> Dict[str, Dict[str, Any]]:
    """Extract server specifications from agent definition. Pure calculation."""
    specs: Dict[str, Dict[str, Any]] = {}
    for name, s in agent.mcp_servers.items():
        if s.transport == "stdio":
            specs[name] = {
                "command": s.command or "python",
                "args": s.args,
                "transport": "stdio",
            }
        elif s.transport == "sse":
            specs[name] = {
                "url": s.url,
                "transport": "sse",
                "headers": s.headers or {},
            }
        else:
            specs[name] = {
                "url": s.url,
                "transport": "streamable_http",
                "headers": s.headers or {},
            }
    return specs


def create_demo_agent(use_plan: bool, mcp_url: str) -> AgentDef:
    """Create a demo agent configuration. Pure calculation."""
    sys = "Be concise. Use tools when helpful."
    servers = {"local": MCPServerCfg(transport="streamable_http", url=mcp_url)}
    tools = ["local:current_date", "local:get_time", "local:code_sandbox"]
    return AgentDef(
        id=f"demo-{'plan' if use_plan else 'react'}",
        system_prompt=sys,
        tools=tools,
        llm=LLMConfig(model=os.getenv("AGENT_MODEL", "gpt-4o-mini"), temperature=0.1),
        run=RunConfig(max_steps=6, timeout_seconds=300),
        use_plan=use_plan,
        mcp_servers=servers,
    )


# ------------------- Azure Table repository (actions with I/O) -------------------


class AgentRepo:
    """Deep module: Simple interface for agent persistence using Azure Tables."""

    def __init__(self, connection_string: str, table: str = "Agents"):
        """Initialize repository with connection string."""
        self.connection_string = connection_string
        self.table = table
        self._svc: Optional[TableServiceClient] = None
        self._tbl = None

    async def _ensure(self) -> None:
        """Ensure table service and table exist."""
        if self._svc is None:
            self._svc = TableServiceClient.from_connection_string(self.connection_string)
        try:
            await self._svc.create_table(self.table)
        except ResourceExistsError:
            pass
        self._tbl = self._svc.get_table_client(self.table)

    async def upsert(self, agent: AgentDef) -> None:
        """Save or update an agent definition."""
        await self._ensure()
        ent = {
            "PartitionKey": agent.partition,
            "RowKey": agent.id,
            "payload": agent.model_dump_json(),
        }
        await self._tbl.upsert_entity(ent, mode=UpdateMode.REPLACE)

    async def get(self, partition: str, agent_id: str) -> AgentDef:
        """Retrieve an agent definition."""
        await self._ensure()
        e = await self._tbl.get_entity(partition_key=partition, row_key=agent_id)
        return AgentDef.model_validate_json(e["payload"])

    async def delete(self, partition: str, agent_id: str) -> None:
        """Delete an agent definition."""
        await self._ensure()
        await self._tbl.delete_entity(partition_key=partition, row_key=agent_id)

    async def list_by_partition(self, partition: str = "Agents") -> List[AgentDef]:
        """List all agents in a partition."""
        await self._ensure()
        out: List[AgentDef] = []
        async for e in self._tbl.query_entities(
            query_filter=f"PartitionKey eq '{partition}'", select="RowKey,payload"
        ):
            out.append(AgentDef.model_validate_json(e["payload"]))
        return out

    async def close(self) -> None:
        """Close the repository and cleanup resources."""
        if self._svc:
            await self._svc.close()


# ------------------- Run manager (stateful actions) -------------------


@dataclass
class RunState:
    """State for a running agent session."""

    session_id: str
    agent_id: str
    status: Literal["running", "done", "timeout", "stopped", "error"] = "running"
    start_ts: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    end_ts: Optional[str] = None
    log: List[LogEvent] = field(default_factory=list)
    queue: asyncio.Queue[LogEvent] = field(default_factory=asyncio.Queue)
    task: Optional[asyncio.Task] = None


# Global state for run management
RUNS: Dict[str, RunState] = {}
RUNS_LOCK = asyncio.Lock()


async def record_log(rs: RunState, node: str, content: Any) -> None:
    """Record a log event to run state. Action - mutates run state."""
    formatted = format_log_content(content)
    ev = create_log_event(node, formatted)
    rs.log.append(ev)
    await rs.queue.put(ev)


# ------------------- Helper functions -------------------


def create_agent_repo() -> AgentRepo:
    """Create agent repository instance from environment."""
    conn_str = os.getenv("ConnectionStrings__tables", "")
    return AgentRepo(conn_str) if conn_str else None


async def seed_demo_agents() -> None:
    """Seed database with demo agents. Action - performs I/O."""
    repo = create_agent_repo()
    if not repo:
        return
    try:
        mcp_url = f"http://localhost:{os.getenv('MCP_PORT', '8765')}/mcp"
        await repo.upsert(create_demo_agent(True, mcp_url))
        await repo.upsert(create_demo_agent(False, mcp_url))
    except Exception as e:
        print(f"Warning: Could not seed demo agents: {e}")
    finally:
        if repo:
            await repo.close()


# ------------------- FastAPI endpoints -------------------


@app.get("/", response_class=fastapi.responses.HTMLResponse)
async def root():
    """Root endpoint with service information."""
    return """
    <h1>Agent MCP Service</h1>
    <p>This service manages AI agents with MCP tool discovery.</p>
    <h2>Available Endpoints:</h2>
    <ul>
        <li><a href='/api/agents'>/api/agents</a> - List all agents</li>
        <li><a href='/api/agents/{agent_id}'>/api/agents/{agent_id}</a> - Get specific agent</li>
        <li><a href='/api/runs'>/api/runs</a> - List active runs</li>
        <li><a href='/api/tools'>/api/tools</a> - List available tools</li>
        <li><a href='/health'>/health</a> - Health check</li>
        <li><a href='/docs'>/docs</a> - API documentation</li>
    </ul>
    """


@app.get("/api/agents", response_model=List[AgentDef])
async def list_agents(partition: str = "Agents"):
    """List all agents in a partition."""
    repo = create_agent_repo()
    if not repo:
        return []
    try:
        return await repo.list_by_partition(partition)
    finally:
        await repo.close()


@app.get("/api/agents/{agent_id}", response_model=AgentDef)
async def get_agent(agent_id: str, partition: str = "Agents"):
    """Get a specific agent by ID."""
    repo = create_agent_repo()
    if not repo:
        raise fastapi.HTTPException(status_code=503, detail="Storage not configured")
    try:
        return await repo.get(partition, agent_id)
    except Exception as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    finally:
        await repo.close()


@app.post("/api/agents", response_model=Dict[str, Any])
async def create_or_update_agent(agent: AgentDef):
    """Create or update an agent."""
    repo = create_agent_repo()
    if not repo:
        raise fastapi.HTTPException(status_code=503, detail="Storage not configured")
    try:
        await repo.upsert(agent)
        return {"ok": True, "id": agent.id}
    finally:
        await repo.close()


@app.delete("/api/agents/{agent_id}", response_model=Dict[str, Any])
async def delete_agent(agent_id: str, partition: str = "Agents"):
    """Delete an agent by ID."""
    repo = create_agent_repo()
    if not repo:
        raise fastapi.HTTPException(status_code=503, detail="Storage not configured")
    try:
        await repo.delete(partition, agent_id)
        return {"ok": True}
    finally:
        await repo.close()


@app.get("/api/runs", response_model=List[RunInfo])
async def list_runs():
    """List all active runs."""
    async with RUNS_LOCK:
        return [
            RunInfo(
                session_id=sid,
                agent_id=rs.agent_id,
                status=rs.status,
                start_ts=rs.start_ts,
                end_ts=rs.end_ts,
                log_len=len(rs.log),
            )
            for sid, rs in RUNS.items()
        ]


@app.get("/api/runs/{session_id}", response_model=RunInfo)
async def get_run_status(session_id: str):
    """Get status of a specific run."""
    rs = RUNS.get(session_id)
    if not rs:
        raise fastapi.HTTPException(status_code=404, detail="Run not found")
    return RunInfo(
        session_id=rs.session_id,
        agent_id=rs.agent_id,
        status=rs.status,
        start_ts=rs.start_ts,
        end_ts=rs.end_ts,
        log_len=len(rs.log),
    )


@app.get("/api/runs/{session_id}/logs", response_model=RunLogsOut)
async def get_run_logs(
    session_id: str, cursor: int = 0, max_items: int = 50, wait_ms: int = 0
):
    """Get logs from a run, optionally waiting for new entries."""
    rs = RUNS.get(session_id)
    if not rs:
        raise fastapi.HTTPException(status_code=404, detail="Run not found")

    # fast path
    if cursor < len(rs.log):
        nxt = min(len(rs.log), cursor + max_items)
        return RunLogsOut(
            lines=rs.log[cursor:nxt],
            next_cursor=nxt,
            done=rs.status in ("done", "timeout", "stopped", "error"),
        )

    # optional wait
    if wait_ms > 0 and rs.status == "running":
        try:
            ev = await asyncio.wait_for(rs.queue.get(), timeout=wait_ms / 1000)
            if not rs.log or rs.log[-1] != ev:
                rs.log.append(ev)
        except asyncio.TimeoutError:
            pass

    nxt = min(len(rs.log), cursor + max_items)
    return RunLogsOut(
        lines=rs.log[cursor:nxt],
        next_cursor=nxt,
        done=rs.status in ("done", "timeout", "stopped", "error"),
    )


@app.post("/api/runs/{session_id}/stop", response_model=Dict[str, Any])
async def stop_run(session_id: str):
    """Stop a running agent."""
    rs = RUNS.get(session_id)
    if not rs or not rs.task:
        raise fastapi.HTTPException(status_code=404, detail="Run not found or not active")
    rs.task.cancel()
    return {"ok": True}


@app.get("/api/tools", response_model=List[ToolRef])
async def list_tools(server: Optional[str] = None, partition: str = "Agents"):
    """List tools available on MCP servers."""
    # Placeholder - full implementation would require MCP client setup
    return []


@app.get("/health", response_class=fastapi.responses.PlainTextResponse)
async def health_check():
    """Health check endpoint."""
    return "Healthy"


# Utility tool endpoints for demonstration
@app.get("/api/utils/time")
async def get_time() -> Dict[str, str]:
    """Get current time in ISO format."""
    return {"time": datetime.now().isoformat(timespec="seconds")}


@app.get("/api/utils/date")
async def current_date(fmt: str = "%Y-%m-%d") -> Dict[str, str]:
    """Get current date with optional format string."""
    from datetime import date

    return {"date": date.today().strftime(fmt)}


@app.post("/api/utils/sandbox")
async def code_sandbox(expr: str) -> Dict[str, str]:
    """Evaluate a safe mathematical expression."""
    allowed = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.Call,
        ast.Load,
        ast.Attribute,
        ast.Name,
        ast.Tuple,
        ast.List,
        ast.Dict,
    }

    def _check_node(n):
        if type(n) not in allowed:
            raise ValueError(f"Bad syntax: {type(n).__name__}")
        for c in ast.iter_child_nodes(n):
            _check_node(c)

    try:
        tree = ast.parse(expr, mode="eval")
        _check_node(tree)
        result = str(
            eval(compile(tree, "<sandbox>", "eval"), {"__builtins__": {}}, {"math": math})
        )
        return {"result": result}
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
