# Quick Start Guide

Get your Python Aspire 13 application running in 5 minutes!

## Prerequisites Check

```bash
# Check .NET version (need 10.0.100+)
dotnet --version

# Check Python version (need 3.13+)
python --version

# Check Node version (need 18+)
node --version

# Check Aspire CLI
aspire --version
```

## Installation (if needed)

### Install .NET 10 SDK

**Linux/macOS:**
```bash
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 10.0
export PATH="$HOME/.dotnet:$PATH"
export DOTNET_ROOT="$HOME/.dotnet"
```

**Windows:**
```powershell
Invoke-WebRequest -Uri https://dot.net/v1/dotnet-install.ps1 -OutFile dotnet-install.ps1
./dotnet-install.ps1 -Channel 10.0
```

### Install Aspire CLI

```bash
dotnet tool install -g Aspire.Cli --prerelease
```

## Run the Application

```bash
cd PythonAspireSample
aspire run
```

That's it! The Aspire dashboard will open automatically showing:
- Python API service
- React frontend
- Azure Storage emulator (Azurite)
- Service health and metrics

## Try the API

Once running, visit these endpoints:

1. **Frontend**: Check the Aspire dashboard for the frontend URL
2. **API Root**: Check dashboard for API URL, then visit `/`
3. **Weather API**: `/api/weatherforecast`
4. **Storage Test**: `/api/storage/test`
5. **Blob Upload**: `/api/blob/upload`
6. **Queue Send**: `/api/queue/send`
7. **Table Insert**: `/api/table/insert`

## Aspire Dashboard

The dashboard (usually at https://localhost:19888) shows:
- ✅ Service health status
- 📊 Real-time metrics
- 📝 Aggregated logs
- 🔍 Distributed traces
- 🌐 Service topology

## Deploy to Azure

```bash
# Using Azure Developer CLI
azd init
azd up

# Or using Aspire CLI (when available)
aspire deploy
```

## Troubleshooting

**Port already in use?**
- Aspire assigns ports dynamically, check the dashboard

**Storage not working?**
- Aspire starts Azurite automatically for local development

**Python errors?**
- Aspire uses `uv` to manage Python dependencies automatically

**Need help?**
- Check the main README.md for detailed documentation
- Run `aspire --help` for CLI commands
- Visit https://aspire.dev for official docs

## What's Next?

1. **Explore the Dashboard** - See real-time telemetry
2. **Try the Storage APIs** - Test blob, queue, and table operations
3. **Customize the App** - Add your own endpoints
4. **Deploy to Azure** - Use `azd up` for one-command deployment

Happy coding! 🚀
