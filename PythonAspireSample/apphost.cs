#:sdk Aspire.AppHost.Sdk@13.0.0
#:package Aspire.Hosting.JavaScript@13.0.0
#:package Aspire.Hosting.Python@13.0.0
#:package Aspire.Hosting.Azure.Storage@13.0.0

var builder = DistributedApplication.CreateBuilder(args);

// Add Azure Storage resources
var storage = builder.AddAzureStorage("storage");
var blobs = storage.AddBlobs("blobs");
var queues = storage.AddQueues("queues");
var tables = storage.AddTables("tables");

var app = builder.AddUvicornApp("app", "./app", "main:app")
    .WithUv()
    .WithReference(blobs)
    .WithReference(queues)
    .WithReference(tables)
    .WithExternalHttpEndpoints()
    .WithHttpHealthCheck("/health");

// Add Agent MCP service
var agentMcp = builder.AddUvicornApp("agent-mcp", "./agent_mcp", "main:app")
    .WithUv()
    .WithReference(tables)
    .WithExternalHttpEndpoints()
    .WithHttpHealthCheck("/health");

var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithReference(app)
    .WaitFor(app);

app.PublishWithContainerFiles(frontend, "./static");

builder.Build().Run();
