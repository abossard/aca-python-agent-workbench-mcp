#!/usr/bin/env bash
# Manual end-to-end test script for Aspire with storage emulation

set -e

echo "=========================================="
echo "Aspire End-to-End Manual Test"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
command -v aspire >/dev/null 2>&1 || { echo "Error: aspire CLI not found. Install with: dotnet tool install -g Aspire.Cli --prerelease"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 not found"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "Error: curl not found"; exit 1; }

echo "✓ Prerequisites found"
echo ""

# Run smoke tests first
echo "Running smoke tests..."
cd "$(dirname "$0")"
python3 -m pytest test_smoke.py -v --tb=short
if [ $? -eq 0 ]; then
    echo "✓ Smoke tests passed"
else
    echo "✗ Smoke tests failed"
    exit 1
fi
echo ""

# Instructions for manual testing
cat << 'EOF'
========================================
Manual Testing Steps
========================================

Now you need to manually test Aspire with the storage emulator:

1. In a NEW terminal window, start Aspire:
   cd ../PythonAspireSample
   aspire run

2. Wait for services to start (~30 seconds)

3. Open Aspire Dashboard:
   https://localhost:18888

4. Check the dashboard for:
   - app service (should be "Healthy")
   - agent-mcp service (should be "Healthy")
   - storage (Azurite - should be running)

5. Note the ports assigned to each service from the dashboard

6. Test the health endpoints:
   curl http://localhost:<app-port>/health
   curl http://localhost:<agent-mcp-port>/health
   
   Both should return "Healthy"

7. Test agent MCP API:
   curl http://localhost:<agent-mcp-port>/api/agents
   curl http://localhost:<agent-mcp-port>/
   
8. Test storage integration:
   curl http://localhost:<app-port>/api/storage/test
   
   Should show all three storage types connected

9. Test agent MCP with Tables:
   # Check if demo agents were seeded
   curl http://localhost:<agent-mcp-port>/api/agents
   
   Should return a list of demo agents

10. When done testing, stop Aspire:
    Ctrl+C in the terminal running Aspire

========================================
Expected Results
========================================

✓ All services start successfully
✓ Health endpoints return "Healthy"
✓ Azurite (storage emulator) is running
✓ Agent MCP can connect to Tables
✓ Demo agents are seeded on startup
✓ No connection errors in logs

If any test fails, check the Aspire dashboard logs for error details.

EOF
