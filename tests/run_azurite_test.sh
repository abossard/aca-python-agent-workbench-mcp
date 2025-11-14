#!/usr/bin/env bash
# Script to run the Azurite integration test
# This demonstrates the full end-to-end test workflow

set -e

echo "=========================================="
echo "Running Azurite Integration Test"
echo "=========================================="
echo ""

# Step 1: Run smoke tests
echo "Step 1: Running smoke tests..."
python3 -m pytest tests/test_smoke.py -v
echo ""
echo "✓ Smoke tests passed!"
echo ""

# Step 2: Instructions for integration test
cat << 'EOF'
========================================
Step 2: Integration Test (Requires Aspire)
========================================

The integration test `test_azurite_create_and_list_agent` requires:
1. Aspire to be running with the full stack
2. Azurite (Azure Tables emulator) to be accessible
3. Agent MCP service to be responding

To run the integration test:

Option A - Manual (Recommended):
---------------------------------
1. In a separate terminal, start Aspire:
   cd PythonAspireSample
   aspire run

2. Wait for services to start (~30 seconds)
   Check Aspire dashboard at: https://localhost:18888

3. Once all services are healthy, run:
   pytest tests/test_integration.py::test_azurite_create_and_list_agent -v -s

Option B - Automated (Takes longer):
------------------------------------
   pytest tests/test_integration.py -v -m integration

   Note: This starts Aspire automatically but takes 30+ seconds

What the test does:
-------------------
1. ✓ Finds the agent-mcp service port
2. ✓ Creates a test agent (POST /api/agents)
   → Writes to Azurite Tables
3. ✓ Lists all agents (GET /api/agents)
   → Reads from Azurite Tables
4. ✓ Retrieves the specific agent (GET /api/agents/{id})
   → Validates data integrity
5. ✓ Deletes the test agent (DELETE /api/agents/{id})
   → Cleanup

This validates the full CRUD cycle with Azure Tables emulator!

========================================
EOF

echo ""
echo "Smoke tests completed successfully!"
echo "See instructions above for running the integration test."
