#!/usr/bin/env bash
# Script to actually run the Azurite integration test with Aspire
set -e

echo "=========================================="
echo "Running Full Azurite Integration Test"
echo "=========================================="
echo ""

# Change to the Aspire directory
cd /home/runner/work/aca-python-agent-workbench-mcp/aca-python-agent-workbench-mcp/PythonAspireSample

echo "Step 1: Starting Aspire in background..."
export PATH="$HOME/.dotnet/tools:$PATH"
export ASPIRE_ALLOW_UNSECURED_TRANSPORT=true
export DOTNET_ENVIRONMENT=Development

# Start Aspire in background
nohup aspire run --non-interactive > ../aspire_output.log 2>&1 &
ASPIRE_PID=$!
echo "Started Aspire with PID: $ASPIRE_PID"
echo ""

# Wait for Aspire to start
echo "Step 2: Waiting for Aspire services to start (30 seconds)..."
sleep 30

# Check if Aspire is still running
if kill -0 $ASPIRE_PID 2>/dev/null; then
    echo "✓ Aspire is running"
else
    echo "✗ Aspire failed to start"
    cat ../aspire_output.log
    exit 1
fi
echo ""

# Wait a bit more for services to be ready
echo "Step 3: Waiting for services to initialize (20 more seconds)..."
sleep 20
echo ""

# Try to find which ports services are on
echo "Step 4: Checking for running services..."
netstat -tuln 2>/dev/null | grep LISTEN | grep -E ":(5000|5001|8000|8080|8765|10002)" || echo "Checking ports..."
echo ""

# Run the actual integration test
echo "Step 5: Running integration test..."
cd /home/runner/work/aca-python-agent-workbench-mcp/aca-python-agent-workbench-mcp
python3 -m pytest tests/test_integration.py::test_azurite_create_and_list_agent -v -s --tb=short 2>&1

TEST_RESULT=$?
echo ""

# Cleanup
echo "Step 6: Stopping Aspire..."
kill $ASPIRE_PID 2>/dev/null || true
sleep 2
kill -9 $ASPIRE_PID 2>/dev/null || true

# Show logs if test failed
if [ $TEST_RESULT -ne 0 ]; then
    echo ""
    echo "=========================================="
    echo "Aspire Logs (last 100 lines):"
    echo "=========================================="
    tail -100 /home/runner/work/aca-python-agent-workbench-mcp/aca-python-agent-workbench-mcp/aspire_output.log
fi

exit $TEST_RESULT
