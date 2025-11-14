# Tests Directory

This directory contains tests for the Python Aspire Agent Workbench project.

## Test Types

### 1. Smoke Tests (test_smoke.py)
Fast, black-box tests that validate:
- Python syntax correctness
- Required imports are present
- Basic structure is valid
- Configuration files exist
- Separation of concerns is documented

### 2. Integration Tests (test_integration.py)
End-to-end tests that start Aspire with the storage emulator:
- Starts full Aspire stack (app, agent_mcp, Azurite)
- Tests health endpoints
- Validates services are accessible
- Checks storage emulator is running

## Running Tests

### Quick Smoke Tests (No Aspire startup required):
```bash
# Install dependencies
pip install pytest pytest-asyncio httpx

# Run smoke tests only
pytest tests/test_smoke.py -v

# Or from tests directory
cd tests
pytest test_smoke.py -v
```

### Integration Tests (Requires Aspire CLI):
```bash
# Install dependencies
pip install pytest pytest-asyncio httpx

# Run integration tests (will start Aspire)
pytest tests/test_integration.py -v -m integration

# WARNING: Integration tests start Aspire which takes ~30 seconds
# They are marked with @pytest.mark.integration
```

### All Tests:
```bash
pytest tests/ -v
```

### Skip Integration Tests:
```bash
pytest tests/ -v -m "not integration"
```

## Manual End-to-End Testing with Aspire

To manually test the full stack with storage emulation:

```bash
# 1. Navigate to PythonAspireSample
cd PythonAspireSample

# 2. Start Aspire (includes Azurite emulator)
aspire run

# 3. Access services via Aspire dashboard
# Dashboard: https://localhost:18888
# Check service URLs and ports in the dashboard

# 4. Test health endpoints
curl http://localhost:<app-port>/health
curl http://localhost:<agent-mcp-port>/health

# 5. Test agent MCP endpoints
curl http://localhost:<agent-mcp-port>/api/agents
curl http://localhost:<agent-mcp-port>/api/runs

# 6. Test storage integration
curl http://localhost:<app-port>/api/storage/test
```

## Test Philosophy

Following the repository's principles:
- **Minimal tests**: Focus on critical paths only
- **Black box**: Test behavior, not implementation
- **Fast**: Smoke tests run in milliseconds
- **Clear failures**: Easy to understand what broke
- **Separation**: Fast smoke tests vs slower integration tests

## CI/CD Integration

The smoke tests are suitable for CI/CD pipelines as they:
- Run in <1 second
- Don't require external services
- Validate code structure and syntax

Integration tests are better suited for:
- Pre-deployment validation
- Manual testing
- Periodic full-stack validation

