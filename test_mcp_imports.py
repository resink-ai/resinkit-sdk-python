#!/usr/bin/env python3
"""Test script to check MCP imports."""

print("Testing MCP imports...")

try:
    from llama_index.tools.mcp import BasicMCPClient
    print('✓ BasicMCPClient import successful')
except ImportError as e:
    print(f'✗ BasicMCPClient import failed: {e}')

try:
    from llama_index.tools.mcp import MCPToolSpec
    print('✓ MCPToolSpec import successful')
except ImportError as e:
    print(f'✗ MCPToolSpec import failed: {e}')

try:
    from llama_index.tools.mcp import McpToolSpec
    print('✓ McpToolSpec import successful')
except ImportError as e:
    print(f'✗ McpToolSpec import failed: {e}')

# Check what's available
try:
    import llama_index.tools.mcp as mcp_module
    available = [x for x in dir(mcp_module) if not x.startswith("_")]
    print(f'Available in mcp module: {available}')
except Exception as e:
    print(f'Error checking module: {e}')

print("Done testing imports.")