# Azure Deployment Guide

Step-by-step guide for deploying your Python Aspire application to Azure Container Apps.

## Prerequisites

- Azure subscription ([Get a free account](https://azure.microsoft.com/free/))
- Azure Developer CLI installed ([Installation guide](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd))
- Azure CLI (optional, for advanced scenarios)

## Deployment Options

### Option 1: Azure Developer CLI (Recommended)

The easiest way to deploy to Azure Container Apps.

#### Step 1: Initialize

```bash
cd /path/to/aca-python-agent-workbench-mcp
azd init
```

This will:
- Scan your project
- Create necessary configuration files
- Set up your deployment environment

#### Step 2: Provision Azure Resources

```bash
azd provision
```

This creates:
- **Azure Container Apps Environment** - Hosting environment for your containers
- **Azure Container Registry** - Private registry for your container images
- **Azure Storage Account** - For Blob, Queue, and Table storage
- **Application Insights** - Application monitoring and telemetry
- **Log Analytics Workspace** - Centralized logging

You'll be prompted to:
1. Select your Azure subscription
2. Choose an Azure region (e.g., `eastus`, `westeurope`)
3. Provide a name for your environment

#### Step 3: Deploy

```bash
azd deploy
```

This will:
- Build container images for Python app and frontend
- Push images to Azure Container Registry
- Deploy to Azure Container Apps
- Configure environment variables and secrets
- Set up service connections

#### Step 4: Access Your Application

```bash
azd show
```

This displays:
- Application URLs
- Service endpoints
- Resource group information
- Azure Portal links

### Option 2: Aspire CLI Deploy (Preview)

When available in Aspire 13:

```bash
cd PythonAspireSample
aspire deploy
```

This will handle the entire deployment process automatically.

## Monitoring Your Application

### View Logs

```bash
# Stream logs in real-time
azd monitor --logs

# Or use Azure CLI
az containerapp logs show --name app --resource-group <rg-name> --follow
```

### Application Insights

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your resource group
3. Open Application Insights resource
4. Explore:
   - Live Metrics
   - Transaction Search
   - Performance metrics
   - Failure analysis
   - Application Map

### Container App Monitoring

1. Azure Portal > Container Apps
2. Select your container app
3. View:
   - Log stream
   - Metrics
   - Revisions
   - Scale settings

## Configuration

### Environment Variables

Azure Container Apps automatically configures:
- `ConnectionStrings__blobs` - Blob storage connection
- `ConnectionStrings__queues` - Queue storage connection
- `ConnectionStrings__tables` - Table storage connection
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OpenTelemetry endpoint

### Secrets Management

For production deployments, use Azure Key Vault:

```bash
# Create Key Vault
az keyvault create --name <vault-name> --resource-group <rg-name>

# Add secrets
az keyvault secret set --vault-name <vault-name> --name "StorageConnectionString" --value "<connection-string>"

# Reference in Container App
az containerapp update --name app --resource-group <rg-name> \
  --set-env-vars "ConnectionStrings__blobs=secretref:StorageConnectionString"
```

## Scaling

### Manual Scaling

```bash
az containerapp update --name app --resource-group <rg-name> \
  --min-replicas 1 \
  --max-replicas 10
```

### Auto-Scaling Rules

Configure in Azure Portal:
1. Container Apps > Your app > Scale
2. Add scaling rules based on:
   - HTTP traffic
   - CPU usage
   - Memory usage
   - Queue length
   - Custom metrics

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install azd
        uses: Azure/setup-azd@v1
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy
        run: azd deploy --no-prompt
        env:
          AZURE_ENV_NAME: ${{ secrets.AZURE_ENV_NAME }}
          AZURE_LOCATION: ${{ secrets.AZURE_LOCATION }}
```

### Azure DevOps

Use Azure Pipelines with the Aspire tasks.

## Cost Management

### Estimated Costs

For a basic deployment:
- **Container Apps**: ~$50-150/month (depends on usage)
- **Azure Storage**: ~$5-20/month
- **Application Insights**: ~$5-30/month (first 5GB free)
- **Container Registry**: ~$5/month (Basic tier)

### Cost Optimization Tips

1. **Use consumption-based pricing** - Container Apps scale to zero
2. **Enable auto-scaling** - Scale down during low traffic
3. **Use appropriate storage tiers** - Cool/Archive for infrequent access
4. **Set up budget alerts** - Monitor and control costs
5. **Review Application Insights sampling** - Reduce data ingestion

## Troubleshooting

### Deployment Fails

```bash
# View detailed logs
azd deploy --debug

# Check resource group
az group show --name <rg-name>

# Check container app status
az containerapp show --name app --resource-group <rg-name>
```

### Application Not Starting

1. Check logs: `azd monitor --logs`
2. Verify environment variables in Azure Portal
3. Check container registry image: `az acr repository show-tags --name <acr-name> --repository app`
4. Review revision status in Azure Portal

### Storage Connection Issues

1. Verify storage account connection strings
2. Check firewall rules on storage account
3. Ensure Managed Identity has correct permissions
4. Test connection from Azure Cloud Shell

### Performance Issues

1. Check Application Insights for slow requests
2. Review CPU/Memory metrics
3. Adjust scaling rules
4. Consider upgrading SKU if needed

## Updating Your Application

```bash
# Make your code changes
git add .
git commit -m "Update application"

# Deploy updated version
azd deploy
```

Aspire/azd will:
- Build new container images
- Create new revision
- Perform zero-downtime deployment
- Roll back automatically if deployment fails

## Cleanup

To remove all Azure resources:

```bash
azd down
```

Or manually in Azure Portal:
1. Navigate to resource group
2. Click "Delete resource group"
3. Confirm deletion

## Best Practices

1. **Use managed identities** - Avoid connection strings in code
2. **Enable diagnostic logs** - Send to Log Analytics
3. **Implement health checks** - Container Apps monitors `/health`
4. **Use Azure Key Vault** - For sensitive configuration
5. **Enable auto-scaling** - Based on your traffic patterns
6. **Set up alerts** - Get notified of issues
7. **Use deployment slots** - Test before production
8. **Implement retry policies** - For resilient storage operations

## Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure Storage Documentation](https://learn.microsoft.com/azure/storage/)
- [Application Insights Documentation](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Aspire Deployment Guide](https://aspire.dev/docs/deployment/)

## Support

- **Azure Support**: [Azure Portal > Help + Support](https://portal.azure.com)
- **Aspire Community**: [GitHub Discussions](https://github.com/dotnet/aspire/discussions)
- **Documentation Issues**: File on GitHub repository

Happy deploying! ☁️
