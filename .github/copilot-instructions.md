# GitHub Copilot Instructions for Python Aspire Agent Workbench

## Project Overview

This is a Python agent workbench built with **Aspire 13** (latest distributed application framework) targeting **Azure Container Apps** deployment. The project integrates **Azure Storage** (Blobs, Queues, Tables) and uses modern cloud-native patterns.

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

#### Azure Storage Integration
- Use environment variables for connection strings: `ConnectionStrings__blobs`, `ConnectionStrings__queues`, `ConnectionStrings__tables`
- Always use `from_connection_string()` for client initialization
- Implement proper error handling for storage operations
- Use context managers when applicable

#### Example Pattern
```python
from azure.storage.blob import BlobServiceClient

blob_connection_string = os.getenv('ConnectionStrings__blobs')
if blob_connection_string:
    blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
    # Use the client
```

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

### Secrets Management
- **Never** hardcode connection strings or secrets
- Use environment variables for all sensitive data
- In production, use Azure Key Vault integration
- Use Managed Identities when possible (Azure SDK supports this)

### Dependency Management
- Run security scans on dependencies regularly
- Keep dependencies up to date (especially security patches)
- Use version constraints to avoid breaking changes

## Common Tasks

### Adding a New Storage Endpoint
1. Add route in `PythonAspireSample/app/main.py`
2. Use environment variable for connection string
3. Implement error handling
4. Add docstring with example response
5. Update README.md with new endpoint

### Adding a New Aspire Resource
1. Update `apphost.cs` with resource definition
2. Use `WithReference()` to inject into Python app
3. Add corresponding connection string handling in Python
4. Update documentation

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
8. **Security first**: Validate inputs, sanitize outputs, use environment variables for secrets

## Questions or Updates

If you're unsure about a pattern or convention:
1. Check existing code in the repository for examples
2. Refer to the comprehensive README.md
3. Consult the QUICKSTART.md for setup procedures
4. Review DEPLOYMENT.md for Azure-specific guidance
