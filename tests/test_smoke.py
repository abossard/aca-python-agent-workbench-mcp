"""
Minimal smoke tests for Python services.

Tests validate:
- Python syntax correctness
- Required imports are present
- Basic structure is valid
- No critical errors in code
"""

import ast
import sys
from pathlib import Path


def test_app_main_syntax():
    """Test that app/main.py has valid Python syntax."""
    app_main = Path(__file__).parent.parent / "PythonAspireSample" / "app" / "main.py"
    assert app_main.exists(), f"File not found: {app_main}"
    
    with open(app_main, 'r') as f:
        content = f.read()
    
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in app/main.py: {e}")


def test_app_main_imports():
    """Test that app/main.py has required imports."""
    app_main = Path(__file__).parent.parent / "PythonAspireSample" / "app" / "main.py"
    
    with open(app_main, 'r') as f:
        content = f.read()
    
    required_imports = ["fastapi", "azure"]
    for imp in required_imports:
        assert f"import {imp}" in content or f"from {imp}" in content, \
            f"Missing required import: {imp}"


def test_agent_mcp_main_syntax():
    """Test that agent_mcp/main.py has valid Python syntax."""
    agent_main = Path(__file__).parent.parent / "PythonAspireSample" / "agent_mcp" / "main.py"
    assert agent_main.exists(), f"File not found: {agent_main}"
    
    with open(agent_main, 'r') as f:
        content = f.read()
    
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in agent_mcp/main.py: {e}")


def test_agent_mcp_main_imports():
    """Test that agent_mcp/main.py has required imports."""
    agent_main = Path(__file__).parent.parent / "PythonAspireSample" / "agent_mcp" / "main.py"
    
    with open(agent_main, 'r') as f:
        content = f.read()
    
    required_imports = ["fastapi", "azure", "pydantic"]
    for imp in required_imports:
        assert f"import {imp}" in content or f"from {imp}" in content, \
            f"Missing required import: {imp}"


def test_agent_mcp_has_health_endpoint():
    """Test that agent_mcp/main.py has a health endpoint."""
    agent_main = Path(__file__).parent.parent / "PythonAspireSample" / "agent_mcp" / "main.py"
    
    with open(agent_main, 'r') as f:
        content = f.read()
    
    assert "/health" in content, "Missing /health endpoint"
    assert "def health_check" in content or "async def health_check" in content, \
        "Missing health_check function"


def test_apphost_has_agent_mcp():
    """Test that apphost.cs includes agent_mcp service."""
    apphost = Path(__file__).parent.parent / "PythonAspireSample" / "apphost.cs"
    assert apphost.exists(), f"File not found: {apphost}"
    
    with open(apphost, 'r') as f:
        content = f.read()
    
    assert "agent-mcp" in content or "agent_mcp" in content, \
        "apphost.cs missing agent_mcp service configuration"


def test_pyproject_files_exist():
    """Test that both services have pyproject.toml files."""
    base = Path(__file__).parent.parent / "PythonAspireSample"
    
    app_pyproject = base / "app" / "pyproject.toml"
    assert app_pyproject.exists(), f"File not found: {app_pyproject}"
    
    agent_pyproject = base / "agent_mcp" / "pyproject.toml"
    assert agent_pyproject.exists(), f"File not found: {agent_pyproject}"


def test_pyproject_has_dependencies():
    """Test that pyproject.toml files have dependencies sections."""
    base = Path(__file__).parent.parent / "PythonAspireSample"
    
    for service in ["app", "agent_mcp"]:
        pyproject = base / service / "pyproject.toml"
        with open(pyproject, 'r') as f:
            content = f.read()
        
        assert "dependencies" in content, \
            f"{service}/pyproject.toml missing dependencies section"
        assert "fastapi" in content, \
            f"{service}/pyproject.toml missing fastapi dependency"


def test_agent_mcp_has_azure_tables():
    """Test that agent_mcp has Azure Tables dependency."""
    agent_pyproject = Path(__file__).parent.parent / "PythonAspireSample" / "agent_mcp" / "pyproject.toml"
    
    with open(agent_pyproject, 'r') as f:
        content = f.read()
    
    assert "azure-data-tables" in content, \
        "agent_mcp/pyproject.toml missing azure-data-tables dependency"
    assert "azure-identity" in content, \
        "agent_mcp/pyproject.toml missing azure-identity dependency"


def test_telemetry_files_exist():
    """Test that both services have telemetry.py files."""
    base = Path(__file__).parent.parent / "PythonAspireSample"
    
    app_telemetry = base / "app" / "telemetry.py"
    assert app_telemetry.exists(), f"File not found: {app_telemetry}"
    
    agent_telemetry = base / "agent_mcp" / "telemetry.py"
    assert agent_telemetry.exists(), f"File not found: {agent_telemetry}"


def test_agent_mcp_structure():
    """Test that agent_mcp has proper code structure with separation of concerns."""
    agent_main = Path(__file__).parent.parent / "PythonAspireSample" / "agent_mcp" / "main.py"
    
    with open(agent_main, 'r') as f:
        content = f.read()
    
    # Check for separation of concerns (pure functions vs actions)
    assert "Pure calculation" in content or "pure function" in content.lower(), \
        "Missing documentation of pure functions"
    
    # Check for proper async usage
    assert "async def" in content, "Missing async functions"
    
    # Check for proper type hints
    assert "from typing import" in content, "Missing typing imports"
    assert "BaseModel" in content, "Missing Pydantic models"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
