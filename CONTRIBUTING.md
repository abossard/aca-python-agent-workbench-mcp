# Contributing to Python Aspire Agent Workbench

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

### Prerequisites

- .NET SDK 10.0.100 or later
- Python 3.13 or later
- Node.js 18+ and npm
- Aspire CLI 13.0.0
- Docker Desktop (for local testing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abossard/aca-python-agent-workbench-mcp.git
   cd aca-python-agent-workbench-mcp
   ```

2. **Install .NET SDK 10 (if needed):**
   ```bash
   curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 10.0
   export PATH="$HOME/.dotnet:$PATH"
   export DOTNET_ROOT="$HOME/.dotnet"
   ```

3. **Install Aspire CLI:**
   ```bash
   dotnet tool install -g Aspire.Cli --prerelease
   ```

4. **Run the application:**
   ```bash
   cd PythonAspireSample
   aspire run
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the coding standards in `.github/copilot-instructions.md`
- Write tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

**Python backend:**
```bash
cd PythonAspireSample/app
uv pip install -e .
pytest  # if tests exist
```

**Frontend:**
```bash
cd PythonAspireSample/frontend
npm install
npm run build
```

**Full integration:**
```bash
cd PythonAspireSample
aspire run
```

### 4. Commit Your Changes

Use conventional commit format:
```bash
git commit -m "feat(api): add new storage endpoint"
git commit -m "fix(frontend): resolve button click issue"
git commit -m "docs: update README with new features"
```

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python

- **Style**: Follow PEP 8
- **Type hints**: Required for all functions
- **Docstrings**: Required for public functions (Google style)
- **Async**: Use `async`/`await` for I/O operations
- **Error handling**: Use try-except blocks for external calls

**Example:**
```python
async def get_blob(container: str, blob_name: str) -> dict:
    """
    Retrieve a blob from Azure Blob Storage.
    
    Args:
        container: Name of the container
        blob_name: Name of the blob to retrieve
        
    Returns:
        Dictionary with blob properties and content
        
    Raises:
        Exception: If blob retrieval fails
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        return {"name": blob_name, "url": blob_client.url}
    except Exception as e:
        logger.error(f"Failed to get blob: {e}")
        raise
```

### TypeScript/React

- **Components**: Use functional components with hooks
- **Types**: Define interfaces for props
- **Naming**: PascalCase for components, camelCase for functions
- **Styling**: Use CSS modules

**Example:**
```typescript
interface WeatherCardProps {
  temperature: number;
  summary: string;
}

const WeatherCard: React.FC<WeatherCardProps> = ({ temperature, summary }) => {
  return (
    <div className="weather-card">
      <h3>{temperature}°C</h3>
      <p>{summary}</p>
    </div>
  );
};
```

### Aspire AppHost

- **Pattern**: Single-file AppHost with top-level statements
- **Resources**: Use builder pattern with `WithReference()`
- **Packages**: Use `#:package` directives

**Example:**
```csharp
#:package Aspire.Hosting.Redis@13.0.0

var redis = builder.AddRedis("redis");

var app = builder.AddUvicornApp("app", "./app", "main:app")
    .WithReference(redis)
    .WithExternalHttpEndpoints();
```

## Adding New Features

### New API Endpoint

1. Add route in `PythonAspireSample/app/main.py`
2. Include docstring with example
3. Add error handling
4. Update README.md
5. Test with Aspire dashboard

### New Aspire Resource

1. Update `apphost.cs` with resource definition
2. Add `WithReference()` to connect to app
3. Handle connection string in Python
4. Update documentation
5. Test locally

### New Frontend Component

1. Create component in `frontend/src/`
2. Add TypeScript types
3. Import in `App.tsx`
4. Test with `npm run dev`
5. Ensure build succeeds

## Testing

### Python Tests

```bash
cd PythonAspireSample/app
pytest tests/
```

### Frontend Tests

```bash
cd PythonAspireSample/frontend
npm run test
```

### Integration Tests

```bash
cd PythonAspireSample
aspire run
# Manually test endpoints
```

## Documentation

### When to Update

- **README.md**: Major features, architecture changes, setup steps
- **QUICKSTART.md**: Quick start procedures
- **DEPLOYMENT.md**: Deployment instructions, Azure configuration
- **API Docs**: New endpoints or changed behavior

### Documentation Style

- Clear and concise
- Include code examples
- Use proper markdown formatting
- Keep up to date with code changes

## Pull Request Guidelines

### PR Title

Use conventional commit format:
```
feat(storage): add queue batch processing
fix(api): resolve connection timeout issue
docs: update Azure deployment guide
```

### PR Description

Include:
- **What**: Brief description of changes
- **Why**: Reason for the changes
- **How**: Technical approach taken
- **Testing**: How you tested the changes
- **Screenshots**: For UI changes (if applicable)

**Template:**
```markdown
## Description
Brief description of the changes

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- Tested locally with `aspire run`
- Verified all endpoints work
- Checked Azure deployment

## Screenshots
(if applicable)
```

### Review Process

1. All PRs require review before merging
2. Address review comments promptly
3. Keep PRs focused and small when possible
4. Ensure CI checks pass

## Code Review Checklist

As a reviewer, check:

- [ ] Code follows project conventions
- [ ] Tests are included (if applicable)
- [ ] Documentation is updated
- [ ] No security issues introduced
- [ ] Error handling is appropriate
- [ ] Commit messages follow convention
- [ ] No breaking changes (or documented)

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Features**: Open an Issue to discuss before implementing
- **Urgent**: Tag maintainers in PR or Issue

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow GitHub's Community Guidelines

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Useful Commands

```bash
# Run locally
cd PythonAspireSample && aspire run

# Install Python dependencies
cd PythonAspireSample/app && uv pip install -e .

# Install frontend dependencies
cd PythonAspireSample/frontend && npm install

# Build frontend
cd PythonAspireSample/frontend && npm run build

# Check Python code style
cd PythonAspireSample/app && ruff check .

# Format Python code
cd PythonAspireSample/app && ruff format .

# Type check Python
cd PythonAspireSample/app && mypy .

# Deploy to Azure
azd up
```

## Resources

- [Aspire Documentation](https://aspire.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [GitHub Copilot Instructions](.github/copilot-instructions.md)

Thank you for contributing! 🎉
