# Agentic AI Project with Strands & MCP

A demonstration project showcasing how to build intelligent agents using Strands Agents framework with Model Context Protocol (MCP) tools and local Ollama models.

## Overview

This project demonstrates the integration of:
- **Strands Agents**: A powerful framework for building AI agents
- **Model Context Protocol (MCP)**: A standardized protocol for tool integration
- **Ollama**: Local LLM inference for privacy and control
- **Custom Tools**: Calculator, addition, and greeting tools via MCP server

## Project Structure

```
agentic AI project/
├── mcp_server/
│   ├── __init__.py
│   └── server.py          # MCP server with custom tools
├── tools/
│   ├── __init__.py
│   └── calculator_tool.py # Calculator tool implementation
├── test_model.py          # Simple model accessibility test
├── strand_with_mcp.py     # Main agent with MCP integration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Features

- **Local LLM Integration**: Uses Ollama for running models locally
- **Tool Calling**: Agents can use tools through MCP protocol
- **Custom Tools**: 
  - Calculator: Evaluate mathematical expressions including sqrt, pow, abs
  - Add: Add two numbers
  - Greet: Greet users by name
- **Extensible Architecture**: Easy to add new tools and capabilities

## Prerequisites

- Python 3.13+
- Ollama installed and running
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
```bash
cd "agentic AI project"
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install strands-agents ollama mcp
```

4. **Install and start Ollama**
```bash
# Install Ollama from https://ollama.com
ollama serve

# Pull required model
ollama pull llama3.2:latest
```

## Usage

### 1. Start the MCP Server

In one terminal:
```bash
python3 -m mcp_server.server
```

### 2. Run the Agent

In another terminal:
```bash
python3 strand_with_mcp.py
```

### 3. Test Model Accessibility

To verify Ollama is working:
```bash
python3 test_model.py
```

## Example Output

```
Testing calculator tool...
Result: The square root of 1764 is 42

Testing add tool...
Result: 25 + 17 = 42

Testing greet tool...
Result: Hello Alice
```

## How It Works

1. **MCP Server**: Exposes tools through the Model Context Protocol
2. **Strands Agent**: Connects to MCP server and uses Ollama for inference
3. **Tool Execution**: Agent decides when to use tools based on user queries
4. **Response Generation**: Agent synthesizes tool results into natural language

## Supported Models

The project works with Ollama models that support tool calling:
- `llama3.2:latest` (2GB) - Recommended
- `llama3.2:1b` (1.3GB) - Faster but less capable
- Other tool-compatible models

## Adding New Tools

1. Add tool function to `mcp_server/server.py`:
```python
@mcp.tool()
def your_tool(param: str) -> str:
    """Tool description"""
    return result
```

2. Restart the MCP server
3. The agent will automatically discover and use the new tool

## Troubleshooting

**Ollama not running**
```bash
ollama serve
```

**Model not found**
```bash
ollama list
ollama pull llama3.2:latest
```

**MCP server connection issues**
- Ensure MCP server is running
- Check that virtual environment is activated
- Verify Python path in `strand_with_mcp.py`

## Technologies Used

- [Strands Agents](https://strandsagents.com/) - Agent framework
- [Ollama](https://ollama.com/) - Local LLM inference
- [Model Context Protocol](https://modelcontextprotocol.io/) - Tool integration standard
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework

## Future Enhancements

- [ ] Add more sophisticated tools (web search, file operations)
- [ ] Implement multi-agent collaboration
- [ ] Add conversation memory
- [ ] Create web interface
- [ ] Add logging and monitoring
- [ ] Implement tool result caching

## Contributing

Contributions are welcome! Feel free to:
- Add new tools
- Improve documentation
- Report bugs
- Suggest features

## License

MIT License - feel free to use this project for learning and development.

## Author

Built with ❤️ to demonstrate the power of local AI agents with tool calling capabilities.

---

**Note**: This project runs entirely locally, ensuring privacy and control over your data.
