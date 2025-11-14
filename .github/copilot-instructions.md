# GitHub Copilot Instructions for Python Aspire Agent Workbench

## Project Overview

This is a Python agent workbench built with **Aspire 13** (latest distributed application framework) targeting **Azure Container Apps** deployment. The project integrates **Azure Storage** (Blobs, Queues, Tables) and uses modern cloud-native patterns.

## Core Coding Principles

This project follows principles from **Grokking Simplicity** and **A Philosophy of Software Design** to create maintainable, understandable code.

> **🔐 CRITICAL SECURITY REQUIREMENT**: Always use `DefaultAzureCredential` from `azure-identity` for all Azure SDK operations. Never use connection strings, access keys, SAS tokens, or any secrets in code, configuration, or environment variables. This is a non-negotiable security requirement.

### From Grokking Simplicity

#### Separate Calculations from Actions and Data
- **Calculations**: Pure functions with no side effects, deterministic, easy to test
  - Example: Data transformations, business logic, validation
  - Always return new data, never mutate inputs
  - Use type hints to make inputs/outputs clear
  
- **Actions**: Functions with side effects (I/O, database, API calls)
  - Mark with `async` keyword for I/O operations
  - Keep minimal - push calculations out
  - Use dependency injection for testability
  
- **Data**: Immutable data structures where possible
  - Use `dataclasses` with `frozen=True` or Pydantic models
  - Prefer returning new objects over mutation

**Example:**
```python
# GOOD: Calculation (pure function)
def calculate_storage_cost(size_gb: float, price_per_gb: float) -> float:
    """Pure calculation - no side effects."""
    return size_gb * price_per_gb

# GOOD: Action clearly marked as async
async def upload_blob(data: bytes, container: str) -> dict:
    """Action with side effects - uploads to storage."""
    blob_client = get_blob_client(container)
    result = await blob_client.upload_blob(data)
    return {"url": blob_client.url, "size": len(data)}
```

#### Focus on Functional Patterns
- **Use map, filter, reduce** instead of loops when transforming data
- **Prefer list/dict comprehensions** for simple transformations
- **Chain operations** for data pipelines
- **Avoid mutation** - create new collections instead

**Example:**
```python
# GOOD: Functional approach
processed_items = [
    transform_item(item)
    for item in items
    if is_valid(item)
]

# GOOD: Using map for transformations
from typing import Callable
results = list(map(transform_item, filter(is_valid, items)))
```

#### Fully Async
- **All I/O operations must be async**: Database, storage, API calls
- **Use `async`/`await` consistently** throughout the codebase
- **Prefer async libraries**: `httpx` over `requests`, `aiofiles` for file I/O
- **Use `asyncio.gather()`** for concurrent operations
- **Never use blocking calls** in async functions

**Example:**
```python
# GOOD: Fully async with concurrent operations
async def fetch_all_storage_data() -> dict:
    """Fetch data from multiple storage sources concurrently."""
    blob_data, queue_data, table_data = await asyncio.gather(
        fetch_blob_data(),
        fetch_queue_data(),
        fetch_table_data()
    )
    return {"blobs": blob_data, "queues": queue_data, "tables": table_data}
```

### From A Philosophy of Software Design

#### Deep and Narrow Modules
- **Deep modules**: Simple interface, powerful implementation
  - Hide complexity behind simple APIs
  - Few public methods, rich functionality
  - Example: A storage client with just `save()` and `load()` but handles retries, compression, etc.

- **Narrow interfaces**: Minimal parameters, clear purpose
  - Avoid "configuration objects" with many options
  - Use sensible defaults, allow overrides only when needed

**Example:**
```python
# GOOD: Deep module - simple interface, complex implementation
class StorageManager:
    """Deep module: Simple API, handles complexity internally."""
    
    async def save(self, key: str, data: bytes) -> str:
        """Save data. Internally handles compression, retries, metadata."""
        compressed = await self._compress(data)
        with_retry = await self._upload_with_retry(compressed)
        await self._update_metadata(key, len(data))
        return with_retry.url
    
    async def load(self, key: str) -> bytes:
        """Load data. Internally handles decompression, caching."""
        cached = await self._check_cache(key)
        if cached:
            return cached
        raw = await self._download(key)
        return await self._decompress(raw)
```

#### Obvious vs Non-Obvious Complexity
- **Make the obvious obvious**: Clear names, simple interfaces
- **Hide non-obvious complexity**: Encapsulate edge cases, error handling
- **Document the non-obvious**: What's not clear from the code
- **Avoid clever code**: Prefer readability over brevity

**Example:**
```python
# BAD: Non-obvious complexity exposed
async def process(d: dict, f: int = 0) -> list:
    return [x for x in d.values() if x > f]

# GOOD: Obvious complexity, clear intent
async def get_active_users(user_data: dict[str, int], min_activity: int = 0) -> list[int]:
    """
    Filter users by activity level.
    
    Args:
        user_data: Mapping of user_id to activity_count
        min_activity: Minimum activity threshold (default: 0)
        
    Returns:
        List of activity counts for active users
    """
    return [
        activity_count 
        for activity_count in user_data.values() 
        if activity_count > min_activity
    ]
```

#### Reduce Number of Parts, Make Relationships Visible
- **Fewer modules, richer functionality**: Combine related functionality
- **Clear dependencies**: Use type hints, dependency injection
- **Avoid deep nesting**: Flatten module hierarchies where possible
- **Make data flow visible**: Use clear parameter names, return types

**Example:**
```python
# GOOD: Clear relationships through type hints and DI
from typing import Protocol

class StorageClient(Protocol):
    async def upload(self, data: bytes) -> str: ...

class DataProcessor:
    """Clear dependency on StorageClient through type hints."""
    
    def __init__(self, storage: StorageClient):
        self.storage = storage
    
    async def process_and_store(self, input_data: dict) -> str:
        """Data flow is visible: dict -> bytes -> str (URL)."""
        processed = self._transform(input_data)  # dict -> dict
        serialized = self._serialize(processed)   # dict -> bytes
        url = await self.storage.upload(serialized)  # bytes -> str
        return url
```

#### Define Errors Out of Existence
- **Make invalid states unrepresentable**: Use type system
- **Provide sensible defaults**: Reduce configuration burden
- **Use optional parameters wisely**: Required params for essential data only
- **Validate at boundaries**: Accept wide, return narrow

**Example:**
```python
# GOOD: Invalid states impossible through design
from enum import Enum
from typing import Literal

class StorageStatus(Enum):
    """Only valid statuses - no magic strings."""
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"

async def upload_with_status(
    data: bytes,
    container: Literal["public", "private"] = "private"
) -> StorageStatus:
    """
    Container can only be 'public' or 'private' - no invalid values possible.
    Returns enum, not string - no parsing errors downstream.
    """
    try:
        await storage.upload(data, container)
        return StorageStatus.UPLOADED
    except Exception:
        return StorageStatus.FAILED
```

#### Pull Complexity Downwards
- **Generic modules at bottom, specific at top**: Library code should be most complex
- **Simple API for common cases**: Hide complexity in base implementation
- **Allow customization without exposure**: Extension points, not configuration
- **Users shouldn't deal with your complexity**: You handle edge cases, retries, errors

**Example:**
```python
# GOOD: Base class handles complexity, users get simple interface
class BaseStorageHandler:
    """Handles all complexity: retries, errors, logging, metrics."""
    
    async def _execute_with_retry(
        self, 
        operation: Callable,
        max_retries: int = 3
    ) -> Any:
        """Complex retry logic hidden in base class."""
        for attempt in range(max_retries):
            try:
                return await operation()
            except TransientError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

class BlobHandler(BaseStorageHandler):
    """Simple interface for users - complexity handled by base."""
    
    async def upload(self, data: bytes) -> str:
        """Simple upload - retry logic automatic."""
        return await self._execute_with_retry(
            lambda: self._do_upload(data)
        )
```

### Modern Python and Async

- **Python 3.13+**: Use latest language features
- **Type hints everywhere**: `from __future__ import annotations`
- **Async by default**: All I/O should be async
- **Use `asyncio` properly**: Understand event loop, tasks, gather
- **Modern syntax**: Pattern matching, structural pattern matching when appropriate
- **Pydantic for data validation**: Not manual checks

**Example:**
```python
from __future__ import annotations
from typing import TypedDict
from pydantic import BaseModel, Field

# GOOD: Modern Python with full async and types
class StorageConfig(BaseModel):
    """Type-safe configuration with validation."""
    container: str = Field(min_length=3, max_length=63)
    max_retries: int = Field(default=3, ge=1, le=10)

async def process_storage_operation(
    config: StorageConfig,
    data: bytes
) -> dict[str, str | int]:
    """Modern async function with full type hints."""
    match config.container:
        case str() if config.container.startswith("temp-"):
            ttl = 3600
        case _:
            ttl = 86400
    
    result = await upload_with_config(data, config, ttl)
    return {"url": result.url, "ttl": ttl, "size": len(data)}
```

### Summary: When Writing Code

1. **Separate concerns**: Calculations (pure) separate from actions (I/O)
2. **Think functionally**: map, filter, comprehensions over loops
3. **Always async**: Never block the event loop
4. **Deep modules**: Simple interface, rich implementation
5. **Obvious code**: Clear names, visible relationships
6. **Type everything**: Use type hints for clarity and safety
7. **Reduce parts**: Combine related functionality
8. **Handle errors**: Don't expose complexity to users
9. **Pull down complexity**: Library code is complex, user code is simple
10. **Modern Python**: Use latest features, full async, Pydantic

## Technology Stack

### Core Technologies
- **Aspire 13**: Latest distributed application framework (.NET 10 SDK required)
- **Python 3.13+**: FastAPI backend with OpenTelemetry
- **React 18 + Vite**: TypeScript frontend
- **Azure Storage SDK**: Blobs, Queues, Tables integration
- **Azure Container Apps**: Serverless container hosting

### Package Managers
- **UV**: For Python dependency management (preferred over pip)
- **npm**: For Node.js/frontend dependencies
- **dotnet**: For .NET tooling

## Coding Standards

### Python (Backend)

#### Style Guide
- Use **async/await** for all I/O operations (FastAPI endpoints)
- Follow **PEP 8** naming conventions (snake_case for functions/variables)
- Use **type hints** for all function parameters and return values
- Generate **docstrings** for all public functions (Google style)
- Use **f-strings** for string formatting (not .format() or %)

#### Dependencies
- Manage dependencies in `pyproject.toml` (not requirements.txt)
- Use UV for package installation: `uv pip install <package>`
- Always specify minimum version constraints: `package>=X.Y.Z`
- **Required Azure packages**: `azure-identity` for all Azure SDK usage
- Azure SDK packages: `azure-storage-blob`, `azure-storage-queue`, `azure-data-tables`, etc.

#### Azure Storage Integration
- **ALWAYS use `DefaultAzureCredential`** - Never use connection strings, secrets, or keys
- Use `azure-identity` package for authentication
- Leverage Managed Identity in Azure environments
- For local development, use Azure CLI or environment-based auth
- Implement proper error handling for storage operations
- Use context managers when applicable

#### Authentication Pattern (REQUIRED)
```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueServiceClient
from azure.data.tables import TableServiceClient

# ALWAYS use DefaultAzureCredential - no connection strings!
credential = DefaultAzureCredential()

# Blob Storage
blob_account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL', 'https://<account>.blob.core.windows.net')
blob_service_client = BlobServiceClient(account_url=blob_account_url, credential=credential)

# Queue Storage
queue_account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL', 'https://<account>.queue.core.windows.net')
queue_service_client = QueueServiceClient(account_url=queue_account_url, credential=credential)

# Table Storage
table_account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL', 'https://<account>.table.core.windows.net')
table_service_client = TableServiceClient(endpoint=table_account_url, credential=credential)
```

#### Why DefaultAzureCredential?
- **Security**: No secrets in code, config, or environment variables
- **Azure Integration**: Automatic Managed Identity support
- **Local Development**: Uses Azure CLI credentials automatically
- **Production Ready**: Same code works locally and in Azure
- **Best Practice**: Microsoft recommended approach

### TypeScript/React (Frontend)

#### Style Guide
- Use **arrow functions** for React components
- Use **functional components** with hooks (no class components)
- Use **TypeScript strict mode** for all files
- Use **CSS modules** or styled-components (not inline styles)
- Use **const** for all variables (not let unless reassignment needed)

#### Naming Conventions
- Components: PascalCase (e.g., `WeatherCard.tsx`)
- Files: kebab-case (e.g., `weather-card.tsx`) or PascalCase matching component
- Props interfaces: ComponentNameProps (e.g., `WeatherCardProps`)

### C# (Aspire AppHost)

#### Style Guide
- Use **single-file AppHost** pattern (`apphost.cs`)
- Use **top-level statements** (no namespace/class wrapping)
- Use **var** for local variable declarations
- Use **#:package** directives for NuGet package references
- Use **builder pattern** for Aspire resource configuration

#### Aspire Patterns
- Always use `WithReference()` to inject connection strings
- Use `WithExternalHttpEndpoints()` for services that need public access
- Use `WithHttpHealthCheck()` to configure health endpoints
- Use `PublishWithContainerFiles()` to bundle frontend into backend container

#### Example Pattern
```csharp
#:package Aspire.Hosting.Azure.Storage@13.0.0

var storage = builder.AddAzureStorage("storage");
var blobs = storage.AddBlobs("blobs");

var app = builder.AddUvicornApp("app", "./app", "main:app")
    .WithReference(blobs)
    .WithExternalHttpEndpoints();
```

## Project Structure

```
/
├── .github/                    # GitHub configuration
│   └── copilot-instructions.md # This file
├── PythonAspireSample/         # Main application
│   ├── apphost.cs              # Aspire 13 single-file AppHost
│   ├── app/                    # Python FastAPI backend
│   │   ├── main.py            # Main API with routes
│   │   ├── telemetry.py       # OpenTelemetry configuration
│   │   └── pyproject.toml     # Python dependencies
│   └── frontend/               # React + Vite frontend
│       ├── src/               # TypeScript source
│       └── package.json       # Node dependencies
├── README.md                   # Main documentation
├── QUICKSTART.md              # 5-minute setup guide
├── DEPLOYMENT.md              # Azure deployment guide
└── azure.yaml                 # Azure Developer CLI config
```

## API Design Patterns

### Endpoint Naming
- Use RESTful conventions: `/api/resource` for collections, `/api/resource/{id}` for items
- Use kebab-case for URL paths: `/api/weather-forecast` (not camelCase)
- Group related endpoints under common prefix: `/api/storage/*`, `/api/blob/*`, `/api/queue/*`, `/api/table/*`

### Response Format
- Return JSON for all API responses
- Use consistent error format: `{"error": "message"}`
- Include status in success responses: `{"status": "success", "data": {...}}`

### Health Checks
- Always implement `/health` endpoint returning plain text "Healthy"
- Use FastAPI's `response_class=fastapi.responses.PlainTextResponse`

## OpenTelemetry Integration

### Tracing
- Instrument FastAPI automatically: `FastAPIInstrumentor.instrument_app(app)`
- Configure in `lifespan` context manager
- Use `telemetry.configure_opentelemetry()` helper function
- Exclude noisy spans: `exclude_spans=["send"]`

### Environment Variables
- `OTEL_EXPORTER_OTLP_ENDPOINT`: Set by Aspire automatically
- `OTEL_SERVICE_NAME`: Service identifier for traces

## Azure Storage Best Practices

### Connection Patterns
- Always check if connection string exists before using
- Use try-except blocks for all storage operations
- Return meaningful error messages to API consumers
- Use `results_per_page` parameter for list operations

### Resource Naming
- Blob containers: lowercase with hyphens (e.g., `test-container`)
- Queues: lowercase with hyphens (e.g., `test-queue`)
- Tables: alphanumeric only (e.g., `testtable`)

### Operations
- Use `upsert_entity()` for tables (not insert which fails on duplicates)
- Use `overwrite=True` for blob uploads in test scenarios
- Include timestamps in entities and messages for debugging

## Aspire CLI Usage

### Development
- Run locally: `aspire run` (from PythonAspireSample directory)
- Create new project: `aspire new aspire-py-starter --name MyProject`
- Add integrations: `aspire add <integration>` (e.g., `aspire add redis`)

### Deployment
- Deploy to Azure: `aspire deploy` (when available)
- Use Azure Developer CLI: `azd up` as alternative

## Testing Guidelines

### Python Tests
- Use `pytest` for all tests
- Place tests in `tests/` directory
- Use `pytest-asyncio` for async tests
- Mock Azure Storage clients using `pytest-mock`

### Frontend Tests
- Use Vitest for unit tests (included with Vite)
- Use React Testing Library for component tests
- Place tests adjacent to components: `Component.test.tsx`

## Documentation Standards

### Code Comments
- Use docstrings for functions, not inline comments for logic
- Include examples in docstrings for complex functions
- Document parameters and return types

### README Updates
- Keep README.md in sync with code changes
- Update API endpoint documentation when adding routes
- Include example usage for new features

### Commit Messages
- Use conventional commits format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Keep subject line under 72 characters
- Include body for complex changes

## Security Considerations

### Azure Authentication (CRITICAL)
- **ALWAYS use `DefaultAzureCredential`** from `azure-identity` package
- **NEVER use connection strings, access keys, or SAS tokens in code**
- **NEVER store secrets in environment variables, config files, or code**
- All Azure SDK clients must use credential-based authentication
- Rely on Managed Identity in Azure environments
- For local dev, use Azure CLI authentication (`az login`)

### Secrets Management
- **No secrets in code**: Use `DefaultAzureCredential` for all Azure resources
- **No secrets in environment variables**: Pass account URLs only, not credentials
- **No secrets in configuration files**: Use identity-based authentication
- Azure Key Vault: Access using `DefaultAzureCredential`, not connection strings

### Example: Secure Azure SDK Usage
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# GOOD: Using DefaultAzureCredential
credential = DefaultAzureCredential()
vault_url = "https://myvault.vault.azure.net"
secret_client = SecretClient(vault_url=vault_url, credential=credential)

# BAD: Never do this!
# connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')  # ❌ NO!
# key = os.getenv('AZURE_STORAGE_KEY')  # ❌ NO!
```

### Dependency Management
- Run security scans on dependencies regularly
- Keep dependencies up to date (especially security patches)
- Use version constraints to avoid breaking changes

## Common Tasks

### Adding a New Storage Endpoint
1. Add route in `PythonAspireSample/app/main.py`
2. **Use `DefaultAzureCredential` for authentication** (never connection strings)
3. Get account URL from environment variable (not secrets)
4. Implement error handling with proper async patterns
5. Add docstring with example response
6. Update README.md with new endpoint

**Example:**
```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

@app.get("/api/blobs/list")
async def list_blobs(container: str) -> dict:
    """List blobs in container using DefaultAzureCredential."""
    credential = DefaultAzureCredential()
    account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL')
    
    blob_service = BlobServiceClient(account_url=account_url, credential=credential)
    container_client = blob_service.get_container_client(container)
    
    blobs = [blob.name async for blob in container_client.list_blobs()]
    return {"container": container, "blobs": blobs}
```

### Adding a New Aspire Resource
1. Update `apphost.cs` with resource definition
2. Use `WithReference()` to inject into Python app
3. **Configure for Managed Identity** (not connection strings)
4. Add corresponding authentication using `DefaultAzureCredential` in Python
5. Update documentation

### Adding Frontend Feature
1. Create component in `PythonAspireSample/frontend/src/`
2. Use TypeScript with proper type definitions
3. Import and use in `App.tsx`
4. Ensure Vite build succeeds

## Environment-Specific Notes

### Local Development
- Aspire automatically starts Azurite (Azure Storage Emulator)
- Dashboard runs at https://localhost:19888 by default
- Hot reload enabled for both Python and frontend

### Azure Deployment
- Connection strings injected by Azure Container Apps
- Managed Identity preferred over connection strings
- Application Insights enabled automatically
- Scale to zero supported

## Performance Considerations

- Use async operations for all I/O in Python
- Implement proper connection pooling for Azure Storage
- Use `uv` for faster Python package installation
- Minimize frontend bundle size (code splitting in Vite)

## Troubleshooting Hints

### Common Issues
- "Aspire CLI requires .NET 10": Install .NET SDK 10.0.100+
- "Storage connection failed": Ensure Azurite is running locally
- "Port already in use": Check Aspire dashboard for assigned ports
- "Python not found": Use Python 3.13+ as specified in `.python-version`

### Debug Mode
- Run with debug output: `aspire run --debug`
- View logs in Aspire dashboard
- Check Application Insights in Azure Portal

## References

- [Aspire 13 Documentation](https://aspire.dev/)
- [Aspire CLI Reference](https://aspire.dev/reference/cli/overview/)
- [Azure Storage Python SDK](https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Container Apps Docs](https://learn.microsoft.com/azure/container-apps/)

## AI Code Generation Preferences

When generating code for this project:

1. **Prefer modern patterns**: Use latest language features and framework patterns
2. **Include error handling**: Always wrap external calls in try-except
3. **Add type hints**: All Python functions should have type annotations
4. **Use async/await**: For FastAPI endpoints and I/O operations
5. **Follow DRY**: Extract common patterns into helper functions
6. **Include examples**: Add docstring examples for complex functions
7. **Consider observability**: Include logging and tracing context
8. **Security first**: 
   - **ALWAYS use `DefaultAzureCredential`** for Azure resources
   - **NEVER use connection strings, keys, or secrets**
   - Validate inputs, sanitize outputs
   - Use identity-based authentication only
9. **Functional approach**: Separate calculations from actions, use map/filter/reduce
10. **Deep modules**: Simple interfaces, complex implementations hidden

## Questions or Updates

If you're unsure about a pattern or convention:
1. Check existing code in the repository for examples
2. Refer to the comprehensive README.md
3. Consult the QUICKSTART.md for setup procedures
4. Review DEPLOYMENT.md for Azure-specific guidance
