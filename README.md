# Python Aspire Agent Workbench with Azure Storage

[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-Ready-brightgreen?logo=github)](https://github.com/features/copilot)
[![Aspire](https://img.shields.io/badge/Aspire-13.0-blue)](https://aspire.dev/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)](https://www.python.org/)
[![.NET](https://img.shields.io/badge/.NET-10.0-purple?logo=dotnet)](https://dotnet.microsoft.com/)

A modern Python agent workbench built with **Aspire 13** for Azure Container Apps deployment, featuring Azure Storage integration (Blobs, Queues, Tables) and MCP (Model Context Protocol) support.

> **🤖 GitHub Copilot Ready**: This repository includes comprehensive [GitHub Copilot instructions](.github/copilot-instructions.md) to help you get the most out of AI-assisted development. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Overview

This project demonstrates a cutting-edge cloud-native Python application using:
- **Aspire 13** (latest) for orchestration and cloud deployment
- **.NET 10 SDK** for Aspire tooling
- **Azure Container Apps** for serverless hosting
- **Azure Storage** (Blobs, Queues, Tables) for data persistence
- **FastAPI** for high-performance REST API
- **React + Vite** frontend with TypeScript
- **OpenTelemetry** for observability
- **MCP** for agent communication

> 📚 **Architecture Documentation**: See [STORAGE_ARCHITECTURE.md](STORAGE_ARCHITECTURE.md) for detailed information about the foundational storage architecture, including multi-tenant data models, partitioning strategies, and query patterns.

## Project Structure

```
.
├── PythonAspireSample/
│   ├── apphost.cs                      # Aspire 13 single-file AppHost
│   ├── apphost.run.json                # Run configuration
│   ├── app/                            # Python FastAPI application
│   │   ├── main.py                     # Main API with Azure Storage endpoints
│   │   ├── telemetry.py                # OpenTelemetry configuration
│   │   ├── pyproject.toml              # Python dependencies
│   │   ├── .python-version             # Python version (3.13)
│   │   └── .dockerignore               # Docker ignore patterns
│   └── frontend/                       # React + Vite frontend
│       ├── src/                        # TypeScript source files
│       ├── public/                     # Static assets
│       ├── vite.config.ts              # Vite configuration
│       └── package.json                # Node dependencies
├── azure.yaml                          # Azure Developer CLI config
└── README.md                           # This file
```

## Prerequisites

### Required
- **.NET SDK 10.0.100 or later** (required for Aspire 13)
- **Python 3.13** or later
- **Node.js 18+** (for frontend)
- **Docker Desktop** or Podman (for local development)

### For Azure Deployment
- **Azure Developer CLI (azd)** - [Install azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- **Azure subscription**

## Getting Started

### 1. Install .NET 10 SDK

**Linux/macOS:**
```bash
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 10.0
export PATH="$HOME/.dotnet:$PATH"
export DOTNET_ROOT="$HOME/.dotnet"
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://dot.net/v1/dotnet-install.ps1 -OutFile dotnet-install.ps1
./dotnet-install.ps1 -Channel 10.0
```

Verify installation:
```bash
dotnet --version  # Should show 10.0.100 or later
```

### 2. Install Aspire CLI 13

Install the Aspire CLI as a .NET global tool:
```bash
dotnet tool install -g Aspire.Cli --prerelease
```

Verify installation:
```bash
aspire --version  # Should show 13.0.0
```

### 3. Run the Application Locally

Navigate to the project directory and run:
```bash
cd PythonAspireSample
aspire run
```

This will:
- Start the Aspire dashboard (typically at https://localhost:19888)
- Launch the Python FastAPI application
- Launch the React frontend
- Set up Azure Storage emulation (Azurite) for local development
- Configure all service connections automatically
- Enable OpenTelemetry tracing and metrics

### 4. Access the Application

Once running, access:
- **Aspire Dashboard**: https://localhost:19888
- **Python API**: http://localhost:PORT (check dashboard for actual port)
- **Frontend**: http://localhost:PORT (check dashboard for actual port)

The dashboard provides:
- Real-time service health monitoring
- Distributed tracing visualization
- Logs aggregation
- Metrics and performance data
- Resource topology

## API Endpoints

The Python FastAPI application provides the following endpoints:

### Core Endpoints
- `GET /` - Service information and available endpoints
- `GET /health` - Health check endpoint
- `GET /api/weatherforecast` - Sample weather forecast data

### Azure Storage Integration Endpoints
- `GET /api/storage/test` - Test all Azure Storage connections
- `GET /api/blob/upload` - Upload a test blob to Azure Blob Storage
- `GET /api/queue/send` - Send a test message to Azure Queue Storage
- `GET /api/table/insert` - Insert a test entity to Azure Table Storage

## Azure Storage Integration

The application demonstrates integration with three Azure Storage services:

### Blob Storage
- Upload and download files
- Container management
- Integrated via `azure-storage-blob` Python SDK
- Connection string: `ConnectionStrings__blobs` (set by Aspire)

### Queue Storage
- Send and receive messages
- Queue management
- Integrated via `azure-storage-queue` Python SDK
- Connection string: `ConnectionStrings__queues` (set by Aspire)

### Table Storage
- NoSQL entity storage
- CRUD operations
- Integrated via `azure-data-tables` Python SDK
- Connection string: `ConnectionStrings__tables` (set by Aspire)

## Aspire CLI Commands

### Creating New Projects
```bash
# Create a new Python Aspire project
aspire new aspire-py-starter --name MyProject --output ./MyProject

# Create just an AppHost
aspire new aspire-apphost-singlefile --name MyAppHost --output ./apphost
```

### Adding Integrations
```bash
# Add PostgreSQL
aspire add postgresql

# Add Redis
aspire add redis

# Add Azure Service Bus
aspire add azure-servicebus
```

### Running and Managing
```bash
# Run in development mode
aspire run

# Run with debug output
aspire run --debug

# Initialize Aspire in existing solution
aspire init
```

### Publishing (Preview)
```bash
# Generate deployment artifacts
aspire publish

# Deploy to Azure Container Apps (Preview)
aspire deploy
```

## Azure Container Apps Deployment

### Using Aspire CLI (Recommended)

1. **Deploy using Aspire CLI** (when available):
   ```bash
   cd PythonAspireSample
   aspire deploy
   ```

### Using Azure Developer CLI (azd)

1. **Initialize the project:**
   ```bash
   azd init
   ```

2. **Provision Azure resources:**
   ```bash
   azd provision
   ```
   This creates:
   - Azure Container Apps Environment
   - Azure Container Registry
   - Azure Storage Account (with Blobs, Queues, Tables)
   - Application Insights
   - Log Analytics workspace

3. **Deploy the application:**
   ```bash
   azd deploy
   ```

4. **View deployment:**
   ```bash
   azd show
   ```

5. **Monitor logs:**
   ```bash
   azd monitor --logs
   ```

## Configuration

### Environment Variables

The Python application reads Azure Storage connection strings from environment variables automatically configured by Aspire:

- `ConnectionStrings__blobs` - Blob storage connection
- `ConnectionStrings__queues` - Queue storage connection  
- `ConnectionStrings__tables` - Table storage connection

### Local Development with Azurite

Aspire automatically manages Azurite (Azure Storage Emulator) for local development. The `apphost.cs` is configured with:

```csharp
var storage = builder
    .AddAzureStorage("storage")
    .RunAsEmulator(azurite =>
    {
        // Ephemeral lifetime for CI/test environments
        azurite.WithLifetime(ContainerLifetime.Ephemeral);
    });
```

This configuration:
- **Local Development**: Automatically starts Azurite in Docker when you run `aspire run`
- **CI/Testing**: Uses session-scoped containers that are removed when the session ends
- **Production**: Switches to real Azure Storage when deployed with `aspire publish`

For manual Azurite testing without Aspire:

```bash
# Install Azurite
npm install -g azurite

# Start Azurite
azurite --silent --location /tmp/azurite

# Connection strings for local emulator
export ConnectionStrings__blobs="UseDevelopmentStorage=true"
export ConnectionStrings__queues="UseDevelopmentStorage=true"
export ConnectionStrings__tables="UseDevelopmentStorage=true"
```

### CI/CD with Azurite Emulation

The project includes GitHub Actions workflows that demonstrate testing against Azurite:

- **`aspire-ci.yml`**: Comprehensive CI testing with Azurite emulation
- **`ui-screenshot.yml`**: UI testing with full stack including storage

Key CI features:
- Automatic Azurite container management via AppHost
- Tests for blob, queue, and table storage operations
- Health checks and service validation
- Proper cleanup of Docker containers

To run AppHost in CI mode:

```bash
cd PythonAspireSample

# Start AppHost with Azurite in non-interactive mode
dotnet run --configuration Release \
  apphost.cs \
  -- \
  --nonInteractive &

# AppHost orchestrates:
# - Azurite Docker container (blob, queue, table services)
# - Python API with storage connections
# - React frontend
```

The AppHost uses `ContainerLifetime.Session` to ensure clean test isolation and automatic cleanup.

## Development

### Installing Python Dependencies

```bash
cd PythonAspireSample/app

# Using uv (recommended by Aspire)
uv pip install -e .

# Or using pip
pip install -e .
```

### Installing Frontend Dependencies

```bash
cd PythonAspireSample/frontend
npm install
```

### Building for Production

```bash
# Frontend
cd PythonAspireSample/frontend
npm run build

# The build output will be served by the Python app in production
```

### Docker Build

Build containers manually:

```bash
# Python app
cd PythonAspireSample/app
docker build -t python-aspire-app .

# Frontend (if needed separately)
cd PythonAspireSample/frontend
docker build -t python-aspire-frontend .
```

## Monitoring and Observability

The project includes comprehensive observability:

- **OpenTelemetry** integration for distributed tracing
- **Structured logging** to Aspire dashboard
- **Health checks** for service monitoring
- **Metrics collection** for performance analysis
- **Aspire Dashboard** for local development insights
- **Azure Application Insights** (when deployed to Azure)
- **Azure Monitor** integration

### Viewing Telemetry

In the Aspire Dashboard, you can:
- View request traces across services
- Monitor service dependencies
- Analyze performance bottlenecks
- Track errors and exceptions
- View logs in real-time

## Troubleshooting

### Common Issues

1. **Aspire CLI requires .NET 10**: Ensure you have .NET SDK 10.0.100 or later installed
   ```bash
   dotnet --version
   ```

2. **Port conflicts**: Aspire assigns ports dynamically. Check the dashboard for actual ports.

3. **Storage connection errors**: 
   - For local dev, Aspire automatically starts Azurite (Azure Storage Emulator)
   - Check the Aspire dashboard to verify Azurite container is running
   - For Azure deployment, verify storage account connection strings

4. **Python version**: Ensure Python 3.13+ is installed
   ```bash
   python --version
   ```

5. **Node.js version**: Ensure Node 18+ is installed for frontend
   ```bash
   node --version
   ```

### Viewing Logs

**Local Development:**
- Use the Aspire Dashboard to view all service logs in one place
- Access at https://localhost:19888

**Azure Deployment:**
- Azure Portal > Container Apps > Log stream
- `azd monitor --logs`
- Application Insights > Transaction search

### Debug Mode

Run with debug output:
```bash
aspire run --debug
```

## Advanced Features

### Single-File AppHost

This project uses Aspire 13's new single-file AppHost format (`apphost.cs`), which provides:
- Simplified project structure
- No need for separate .csproj files
- Inline package references using `#:package` directives
- Easier to understand and maintain

### Azure Storage Emulation with RunAsEmulator

The AppHost uses Aspire 13's `RunAsEmulator()` pattern for Azure Storage:

```csharp
var storage = builder
    .AddAzureStorage("storage")
    .RunAsEmulator(azurite =>
    {
        // Session lifetime for CI/test environments
        azurite.WithLifetime(ContainerLifetime.Session);
    });
```

Benefits:
- **Development**: Automatically runs Azurite in Docker locally
- **CI/Testing**: Uses session-scoped containers for isolated testing
- **Production**: Seamlessly switches to real Azure Storage on deployment
- **No code changes**: Same app code works in all environments

The emulator provides full blob, queue, and table storage services for local development and testing.

### UV Package Manager

The Python app uses `uv` for fast package management:
- Significantly faster than pip
- Better dependency resolution
- Integrated with Aspire

### Container Files Publishing

The frontend is published into the Python app's static directory using:
```csharp
app.PublishWithContainerFiles(frontend, "./static");
```

This creates a single container with both frontend and backend.

## Contributing

Contributions are welcome! This repository is **GitHub Copilot Ready** with comprehensive instructions to help you contribute effectively.

### Getting Started with GitHub Copilot

This repository includes:
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Project-specific Copilot instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Detailed contribution guidelines
- **[.vscode/settings.json](.vscode/settings.json)** - VS Code configuration optimized for Copilot
- **[.editorconfig](.editorconfig)** - Consistent code style across editors

GitHub Copilot will automatically use these instructions to provide better suggestions tailored to this project's patterns and conventions.

### Contributing Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes (Copilot will help with context-aware suggestions)
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Resources

### Documentation
- [Storage Architecture](STORAGE_ARCHITECTURE.md) - Multi-tenant storage design with Azure Storage services
- [Deployment Guide](DEPLOYMENT.md) - Azure Container Apps deployment
- [Quick Start](QUICKSTART.md) - 5-minute setup guide
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

### External Resources
- [Aspire 13 Documentation](https://aspire.dev/)
- [Aspire CLI Overview](https://aspire.dev/reference/cli/overview/)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [Azure Storage Python SDK](https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

## License

This project is open source and available under the MIT License.
