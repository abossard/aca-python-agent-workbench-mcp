#!/bin/bash
# Script to test Aspire AppHost with Azurite emulation locally
# This simulates what happens in CI

set -e

echo "=== Aspire AppHost Test Script ==="
echo ""

# Change to PythonAspireSample directory
cd "$(dirname "$0")/PythonAspireSample"

# Check prerequisites
echo "Checking prerequisites..."
dotnet --version || { echo "ERROR: .NET 10 SDK not found"; exit 1; }
docker --version || { echo "ERROR: Docker not found"; exit 1; }
echo "✓ Prerequisites OK"
echo ""

# Clean up any existing processes/containers
echo "Cleaning up existing processes..."
pkill -f "dotnet.*apphost" || true
docker stop $(docker ps -q --filter "name=azurite") 2>/dev/null || true
sleep 2
echo "✓ Cleanup complete"
echo ""

# Build the apphost
echo "Building AppHost..."
if ! dotnet build apphost.cs --configuration Release; then
    echo "ERROR: AppHost build failed"
    exit 1
fi
echo "✓ Build successful"
echo ""

# Start AppHost in background
echo "Starting AppHost with Azurite emulation..."
dotnet run --configuration Release \
  --project apphost.cs \
  --no-build \
  -- \
  --non-interactive > aspire_test.log 2>&1 &

ASPIRE_PID=$!
echo "Started AppHost with PID: $ASPIRE_PID"
echo ""

# Give it time to start containers
echo "Waiting for services to initialize (30 seconds)..."
sleep 30

# Check if process is still running
if ! kill -0 $ASPIRE_PID 2>/dev/null; then
    echo "ERROR: AppHost process died!"
    echo ""
    echo "=== Log Output ==="
    cat aspire_test.log
    exit 1
fi
echo "✓ AppHost process is running"
echo ""

# Check Docker containers
echo "Checking Docker containers..."
if docker ps | grep -q azurite; then
    echo "✓ Azurite container is running"
    docker ps --filter "name=azurite" --format "table {{.Names}}\t{{.Status}}"
else
    echo "WARNING: Azurite container not found"
    echo "All containers:"
    docker ps
fi
echo ""

# Try to access Aspire dashboard
echo "Checking Aspire dashboard..."
max_attempts=30
attempt=0
dashboard_ready=false

while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:18888 > /dev/null 2>&1; then
        echo "✓ Aspire dashboard is accessible at http://localhost:18888"
        dashboard_ready=true
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ "$dashboard_ready" = false ]; then
    echo "WARNING: Dashboard not accessible after 60 seconds"
fi
echo ""

# Cleanup
echo "Cleaning up..."
kill $ASPIRE_PID 2>/dev/null || true
sleep 3
kill -9 $ASPIRE_PID 2>/dev/null || true
docker stop $(docker ps -q --filter "name=azurite") 2>/dev/null || true
echo "✓ Cleanup complete"
echo ""

echo "=== Test Summary ==="
if [ "$dashboard_ready" = true ]; then
    echo "✓ AppHost test PASSED"
    echo ""
    echo "To run the application normally, use:"
    echo "  cd PythonAspireSample"
    echo "  dotnet run --project apphost.cs"
    exit 0
else
    echo "✗ AppHost test FAILED"
    echo ""
    echo "=== Last 50 lines of log ==="
    tail -50 aspire_test.log
    exit 1
fi
