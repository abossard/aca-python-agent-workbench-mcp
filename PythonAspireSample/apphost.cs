#:sdk Aspire.AppHost.Sdk@13.0.0
#:package Aspire.Hosting.JavaScript@13.0.0
#:package Aspire.Hosting.Python@13.0.0
#:package Aspire.Hosting.Azure.Storage@13.0.0

using Aspire.Hosting;
using Aspire.Hosting.Azure;

var builder = DistributedApplication.CreateBuilder(args);

// Add Azure Storage resources with emulator support for local/CI environments
// RunAsEmulator configures Azurite (Azure Storage Emulator) in Docker for "run" mode
// but keeps real Azure resources for "publish" mode
var storage = builder
    .AddAzureStorage("storage")
    .RunAsEmulator(azurite =>
    {
        // Session lifetime for CI/test environments - container is removed when session ends
        azurite.WithLifetime(ContainerLifetime.Session);
        // Note: Use WithDataVolume("azurite-data") for persistent local development if needed
    });

var blobs = storage.AddBlobs("blobs");
var queues = storage.AddQueues("queues");
var tables = storage.AddTables("tables");

var app = builder.AddUvicornApp("app", "./app", "main:app")
    .WithUv()
    .WithReference(blobs)
    .WithReference(queues)
    .WithReference(tables)
    .WithExternalHttpEndpoints()
    .WithHttpHealthCheck("/health")
    .WaitFor(storage);  // Ensure storage is ready before starting app

var frontend = builder.AddViteApp("frontend", "./frontend")
    .WithReference(app)
    .WaitFor(app);

app.PublishWithContainerFiles(frontend, "./static");

builder.Build().Run();
