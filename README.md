# Python Aspire Agent Workbench with MCP

A Python agent workbench built with .NET Aspire for Azure Container Apps deployment, featuring Azure Storage integration (Blobs, Queues, Tables) and MCP (Model Context Protocol) support.

## Overview

This project demonstrates a modern cloud-native Python application using:
- **.NET Aspire** for orchestration and deployment
- **Azure Container Apps** for hosting
- **Azure Storage** (Blobs, Queues, Tables) for data persistence
- **Flask** for the REST API
- **MCP** for agent communication

## Project Structure

```
.
├── PythonAspireSample.AppHost/       # .NET Aspire orchestrator
│   ├── Program.cs                     # Aspire app configuration
│   └── PythonAspireSample.AppHost.csproj
├── PythonAspireSample.ServiceDefaults/ # Shared service defaults
│   ├── Extensions.cs                  # OpenTelemetry & health checks
│   └── PythonAspireSample.ServiceDefaults.csproj
├── python-app/                        # Python Flask application
│   ├── app.py                         # Main application
│   ├── requirements.txt               # Python dependencies
│   └── Dockerfile                     # Container image
├── azure.yaml                         # Azure Developer CLI config
└── PythonAspireSample.sln            # Visual Studio solution
```

## Prerequisites

- **.NET 9.0 SDK** or later
- **Python 3.12** or later
- **Docker Desktop** or Podman
- **Azure Developer CLI (azd)** - for Azure deployment
- **Azure subscription** (for cloud deployment)

## Local Development Setup

### 1. Install Dependencies

Install .NET Aspire workload (if not already installed):
```bash
dotnet workload install aspire
```

Install Python dependencies:
```bash
cd python-app
pip install -r requirements.txt
```

### 2. Run with Aspire

Start the application using Aspire:
```bash
dotnet run --project PythonAspireSample.AppHost/PythonAspireSample.AppHost.csproj
```

This will:
- Start the Aspire dashboard (typically at https://localhost:15888)
- Launch the Python application
- Set up Azure Storage emulation (Azurite) for local development
- Configure all service connections automatically

### 3. Access the Application

Once running, access:
- **Aspire Dashboard**: https://localhost:15888
- **Python App**: http://localhost:8000

## API Endpoints

The Python application provides the following endpoints:

- `GET /` - Service information and available endpoints
- `GET /health` - Health check endpoint
- `GET /storage/test` - Test Azure Storage connections
- `GET /blob/upload` - Test blob upload operation
- `GET /queue/send` - Test queue message send
- `GET /table/insert` - Test table entity insert

## Azure Storage Integration

The application demonstrates integration with three Azure Storage services:

### Blob Storage
- Upload and download files
- Container management
- Connection via `azure-storage-blob` Python SDK

### Queue Storage
- Send and receive messages
- Queue management
- Connection via `azure-storage-queue` Python SDK

### Table Storage
- NoSQL entity storage
- CRUD operations
- Connection via `azure-data-tables` Python SDK

## Azure Container Apps Deployment

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
   - Logging and monitoring resources

3. **Deploy the application:**
   ```bash
   azd deploy
   ```

4. **Access your deployed app:**
   ```bash
   azd show
   ```

### Manual Deployment

Alternatively, use Aspire's built-in deployment:
```bash
dotnet publish PythonAspireSample.AppHost/PythonAspireSample.AppHost.csproj
```

Then deploy the generated manifests to Azure.

## Configuration

### Environment Variables

The Python application reads Azure Storage connection strings from environment variables:
- `ConnectionStrings__blobs` - Blob storage connection
- `ConnectionStrings__queues` - Queue storage connection
- `ConnectionStrings__tables` - Table storage connection

These are automatically configured by Aspire during local development and Azure deployment.

### Local Development

For local testing without Aspire, you can use Azurite (Azure Storage Emulator):
```bash
# Install Azurite
npm install -g azurite

# Start Azurite
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log

# Set connection strings to local emulator
export ConnectionStrings__blobs="UseDevelopmentStorage=true"
export ConnectionStrings__queues="UseDevelopmentStorage=true"
export ConnectionStrings__tables="UseDevelopmentStorage=true"
```

## Development

### Building the Project

Build the .NET projects:
```bash
dotnet build PythonAspireSample.sln
```

### Running Tests

```bash
# Run Python tests (if available)
cd python-app
pytest

# Run .NET tests (if available)
dotnet test
```

### Docker Build

Build the Python app container:
```bash
cd python-app
docker build -t python-aspire-app .
docker run -p 8000:8000 python-aspire-app
```

## Monitoring and Observability

The project includes:
- **OpenTelemetry** integration for distributed tracing
- **Health checks** for service monitoring
- **Aspire Dashboard** for local development insights
- **Azure Application Insights** (when deployed to Azure)

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000 and 15888 are available
2. **Storage connection errors**: Verify Azurite is running for local dev
3. **Python not found**: Ensure Python 3.12+ is in your PATH
4. **.NET Aspire workload**: Run `dotnet workload install aspire`

### Logs

View logs through:
- Aspire Dashboard (local development)
- Azure Portal > Container Apps > Log stream (Azure deployment)
- `azd monitor --logs` command

## Contributing

Contributions are welcome! Please submit issues and pull requests.

## License

This project is open source and available under the MIT License.

## Resources

- [.NET Aspire Documentation](https://learn.microsoft.com/en-us/dotnet/aspire/)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Storage Python SDK](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Flask Documentation](https://flask.palletsprojects.com/)
