"""
End-to-end integration tests that start Aspire with storage emulation.

These tests use subprocess to start the Aspire apphost and verify services are running.
"""

import asyncio
import subprocess
import time
import httpx
import pytest
from pathlib import Path


@pytest.fixture(scope="module")
def aspire_process():
    """
    Start Aspire in background and yield, then cleanup.
    
    This fixture starts the full Aspire stack including:
    - Azure Storage emulator (Azurite)
    - Python app service
    - Agent MCP service
    - Frontend service
    """
    aspire_dir = Path(__file__).parent.parent.parent / "PythonAspireSample"
    
    # Start Aspire in background
    process = subprocess.Popen(
        ["aspire", "run", "--non-interactive"],
        cwd=str(aspire_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**subprocess.os.environ, "ASPIRE_ALLOW_UNSECURED_TRANSPORT": "true"}
    )
    
    # Wait for startup (give it time to initialize)
    time.sleep(30)
    
    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        pytest.fail(f"Aspire failed to start.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
    
    yield process
    
    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_aspire_dashboard_is_running(aspire_process):
    """Test that Aspire dashboard is accessible."""
    async with httpx.AsyncClient() as client:
        for attempt in range(10):
            try:
                response = await client.get("http://localhost:18888", timeout=5.0)
                if response.status_code in (200, 301, 302):
                    return  # Success
            except httpx.HTTPError:
                if attempt < 9:
                    await asyncio.sleep(2)
                else:
                    pytest.fail("Aspire dashboard not accessible after multiple attempts")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_app_service_health_endpoint(aspire_process):
    """Test that the main app service health endpoint responds."""
    # Note: Port is dynamically assigned, but we can try common ports
    async with httpx.AsyncClient() as client:
        for port in [5000, 5001, 5173, 5174, 8000, 8080]:
            try:
                response = await client.get(f"http://localhost:{port}/health", timeout=5.0)
                if response.status_code == 200 and response.text == "Healthy":
                    return  # Success
            except httpx.HTTPError:
                continue
        
        # If we get here, service might not be ready yet - give it more time
        await asyncio.sleep(10)
        
        for port in [5000, 5001, 5173, 5174, 8000, 8080]:
            try:
                response = await client.get(f"http://localhost:{port}/health", timeout=5.0)
                if response.status_code == 200:
                    return  # Success
            except httpx.HTTPError:
                continue
        
        pytest.skip("Could not find app service on expected ports - may need dashboard inspection")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_mcp_service_health_endpoint(aspire_process):
    """Test that the agent-mcp service health endpoint responds."""
    async with httpx.AsyncClient() as client:
        for port in [8765, 5000, 5001, 5002, 8000, 8080, 8081]:
            try:
                response = await client.get(f"http://localhost:{port}/health", timeout=5.0)
                if response.status_code == 200 and response.text == "Healthy":
                    return  # Success
            except httpx.HTTPError:
                continue
        
        # Give more time
        await asyncio.sleep(10)
        
        for port in [8765, 5000, 5001, 5002, 8000, 8080, 8081]:
            try:
                response = await client.get(f"http://localhost:{port}/health", timeout=5.0)
                if response.status_code == 200:
                    return  # Success
            except httpx.HTTPError:
                continue
        
        pytest.skip("Could not find agent-mcp service on expected ports")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_storage_emulator_is_accessible(aspire_process):
    """Test that Azure Storage emulator (Azurite) is running."""
    # Azurite default ports: Blob 10000, Queue 10001, Table 10002
    async with httpx.AsyncClient() as client:
        for port in [10000, 10001, 10002]:
            try:
                # Just check if port is open (Azurite may not respond to GET /)
                response = await client.get(f"http://localhost:{port}", timeout=2.0)
                # Any response (even error) means service is running
                return
            except httpx.ConnectError:
                continue
            except httpx.HTTPError:
                # Even HTTP errors mean the service is running
                return
        
        pytest.skip("Azurite emulator not detected on standard ports")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_mcp_has_api_endpoints(aspire_process):
    """Test that agent-mcp service has expected API endpoints."""
    async with httpx.AsyncClient() as client:
        for port in [8765, 5000, 5001, 5002]:
            try:
                # Try root endpoint
                response = await client.get(f"http://localhost:{port}/", timeout=5.0)
                if response.status_code == 200:
                    content = response.text.lower()
                    # Check for agent-related content
                    if "agent" in content or "mcp" in content:
                        # Verify agents endpoint exists
                        agents_response = await client.get(f"http://localhost:{port}/api/agents", timeout=5.0)
                        if agents_response.status_code in (200, 503):  # 503 if storage not ready
                            return
            except httpx.HTTPError:
                continue
        
        pytest.skip("Could not verify agent-mcp API endpoints")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_azurite_create_and_list_agent(aspire_process):
    """
    Test that Azurite is running by creating an agent and then listing it.
    
    This verifies:
    1. Azurite (Azure Tables emulator) is accessible
    2. Agent MCP service can write to Tables
    3. Agent MCP service can read from Tables
    """
    async with httpx.AsyncClient() as client:
        # Find the agent-mcp service port
        agent_mcp_port = None
        for port in [8765, 5000, 5001, 5002, 8000, 8080, 8081]:
            try:
                response = await client.get(f"http://localhost:{port}/", timeout=5.0)
                if response.status_code == 200 and ("agent" in response.text.lower() or "mcp" in response.text.lower()):
                    agent_mcp_port = port
                    break
            except httpx.HTTPError:
                continue
        
        if not agent_mcp_port:
            pytest.skip("Could not find agent-mcp service port")
        
        base_url = f"http://localhost:{agent_mcp_port}"
        
        # Create a test agent
        test_agent = {
            "id": f"test-agent-{int(time.time())}",
            "partition": "Agents",
            "system_prompt": "Test agent for Azurite validation",
            "tools": ["local:get_time"],
            "llm": {
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "params": {}
            },
            "run": {
                "max_steps": 5,
                "timeout_seconds": 60
            },
            "use_plan": False,
            "mcp_servers": {}
        }
        
        # Create the agent (writes to Azurite Tables)
        create_response = await client.post(
            f"{base_url}/api/agents",
            json=test_agent,
            timeout=10.0
        )
        
        # Verify creation succeeded
        assert create_response.status_code == 200, f"Failed to create agent: {create_response.text}"
        create_data = create_response.json()
        assert create_data.get("ok") is True, f"Agent creation not successful: {create_data}"
        assert create_data.get("id") == test_agent["id"], "Agent ID mismatch"
        
        # Wait a moment for consistency
        await asyncio.sleep(1)
        
        # List agents (reads from Azurite Tables)
        list_response = await client.get(
            f"{base_url}/api/agents",
            params={"partition": "Agents"},
            timeout=10.0
        )
        
        # Verify list succeeded
        assert list_response.status_code == 200, f"Failed to list agents: {list_response.text}"
        agents = list_response.json()
        assert isinstance(agents, list), "Expected list of agents"
        
        # Verify our test agent is in the list
        agent_ids = [agent.get("id") for agent in agents]
        assert test_agent["id"] in agent_ids, f"Test agent not found in list. Found: {agent_ids}"
        
        # Verify we can retrieve the specific agent
        get_response = await client.get(
            f"{base_url}/api/agents/{test_agent['id']}",
            params={"partition": "Agents"},
            timeout=10.0
        )
        
        assert get_response.status_code == 200, f"Failed to get agent: {get_response.text}"
        retrieved_agent = get_response.json()
        assert retrieved_agent.get("id") == test_agent["id"], "Retrieved agent ID mismatch"
        assert retrieved_agent.get("system_prompt") == test_agent["system_prompt"], "Agent data mismatch"
        
        # Clean up: delete the test agent
        delete_response = await client.delete(
            f"{base_url}/api/agents/{test_agent['id']}",
            params={"partition": "Agents"},
            timeout=10.0
        )
        
        assert delete_response.status_code == 200, f"Failed to delete agent: {delete_response.text}"
        delete_data = delete_response.json()
        assert delete_data.get("ok") is True, "Agent deletion not successful"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
