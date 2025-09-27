# MCP Clients

This directory contains all MCP (Model Context Protocol) client implementations for Sparkflow.

## Structure

```
mcp_clients/
├── __init__.py          # Package initialization
├── base_client.py       # Base class for all MCP clients
├── resend_client.py     # Resend email MCP client
└── README.md           # This file
```

## Available Clients

### Resend Client (`resend_client.py`)
- **Purpose**: Send emails via Resend MCP server
- **Features**: HTML/text email support, fallback to HTTP
- **Usage**: `from src.mcp_clients import MCPResendClient`

## Adding New MCP Clients

1. **Create a new client file** (e.g., `github_client.py`)
2. **Inherit from BaseMCPClient**:
   ```python
   from .base_client import BaseMCPClient
   
   class MCPGitHubClient(BaseMCPClient):
       # Implement required methods
   ```
3. **Add to `__init__.py`**:
   ```python
   from .github_client import MCPGitHubClient
   __all__ = ['MCPResendClient', 'MCPGitHubClient']
   ```
4. **Register in orchestrator**:
   ```python
   # In mcp_orchestrator.py
   self.clients = {
       'resend': MCPResendClient(self.config),
       'github': MCPGitHubClient(self.config),  # Add here
   }
   ```

## MCP Server Setup

Each MCP client requires a corresponding MCP server to be set up:

1. **Install MCP server** (usually via npm)
2. **Configure server** with API keys
3. **Update client** to point to correct server path
4. **Test integration** with the orchestrator

## Best Practices

- **Error Handling**: Always include fallback mechanisms
- **Logging**: Use consistent logging format
- **Configuration**: Use config object for all settings
- **Testing**: Include test cases for each client
- **Documentation**: Document all public methods
