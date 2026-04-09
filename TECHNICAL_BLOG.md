# Building Local AI Agents: A Deep Dive into Strands, Ollama, and MCP Integration

## Introduction

In this comprehensive guide, we'll build a fully local AI agent system that combines three powerful technologies: Strands Agents framework, Ollama for local LLM inference, and the Model Context Protocol (MCP) for tool integration. By the end, you'll understand how these components work together and when to use different MCP transport mechanisms.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Strands Agent                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Agent Logic & Orchestration                         │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                              │                   │
│           ▼                              ▼                   │
│  ┌─────────────────┐          ┌──────────────────┐          │
│  │  Ollama Model   │          │   MCP Client     │          │
│  │  (llama3.2)     │          │   (STDIO)        │          │
│  └─────────────────┘          └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
    ┌──────────────┐           ┌──────────────────┐
    │   Ollama     │           │   MCP Server     │
    │   Server     │           │   (FastMCP)      │
    │ :11434       │           │   STDIO          │
    └──────────────┘           └──────────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │  Custom Tools   │
                               │  - Calculator   │
                               │  - Add          │
                               │  - Greet        │
                               └─────────────────┘
```

## Part 1: Setting Up Ollama (Local LLM)

### What is Ollama?

Ollama is a local LLM runtime that allows you to run large language models on your machine without sending data to external APIs. This ensures privacy, reduces latency, and eliminates API costs.

### Step 1: Install Ollama

```bash
# Download and install from https://ollama.com
# For Linux:
curl -fsSL https://ollama.com/install.sh | sh

# For macOS:
brew install ollama

# For Windows:
# Download installer from ollama.com
```

### Step 2: Start Ollama Server

```bash
# Start the Ollama service (runs on port 11434 by default)
ollama serve
```

The Ollama server exposes a REST API at `http://localhost:11434` that accepts requests in OpenAI-compatible format.

### Step 3: Pull a Model

```bash
# Pull llama3.2 (2GB) - supports tool calling
ollama pull llama3.2:latest

# Alternative: smaller model (1.3GB)
ollama pull llama3.2:1b

# Verify installation
ollama list
```

### Step 4: Test Ollama Directly

```bash
# Interactive chat
ollama run llama3.2:latest

# Or via API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:latest",
  "prompt": "What is 2+2?"
}'
```

### Why Ollama for This Project?

- **Privacy**: All data stays local
- **Tool Calling Support**: llama3.2 supports function calling
- **OpenAI-Compatible API**: Easy integration with frameworks
- **Resource Efficient**: Runs on consumer hardware

## Part 2: Understanding Model Context Protocol (MCP)

### What is MCP?

Model Context Protocol is a standardized protocol for connecting AI models to external tools and data sources. Think of it as a universal adapter that allows any AI agent to use any tool, regardless of implementation.

### MCP Architecture Components

1. **MCP Server**: Exposes tools/resources via standardized protocol
2. **MCP Client**: Connects to servers and invokes tools
3. **Transport Layer**: Communication mechanism (STDIO or HTTP)

### STDIO vs HTTP Transport: When to Use Each

#### STDIO Transport (Standard Input/Output)

**How it works:**
- MCP server runs as a subprocess
- Communication via stdin/stdout pipes
- Client spawns server process and manages lifecycle

**Use STDIO when:**
- Running locally on the same machine
- You want automatic process management
- Tools need access to local filesystem
- Security is handled by OS process isolation
- You need low latency (no network overhead)

**Advantages:**
- No network configuration needed
- Automatic process lifecycle management
- Lower latency than HTTP
- Better for development and testing

**Example Use Cases:**
- Local file operations
- Database queries on localhost
- System utilities
- Development environments

#### HTTP Transport

**How it works:**
- MCP server runs as HTTP service
- Communication via REST API
- Client connects to server URL

**Use HTTP when:**
- Server runs on different machine
- Multiple clients need to share tools
- You need load balancing/scaling
- Tools are deployed as microservices
- You want language-agnostic integration

**Advantages:**
- Network-accessible (remote tools)
- Multiple concurrent clients
- Standard web infrastructure (load balancers, proxies)
- Language agnostic

**Example Use Cases:**
- Production deployments
- Shared tool services
- Cloud-hosted tools
- Multi-agent systems

### Our Project Uses STDIO

We use STDIO because:
1. Everything runs locally on one machine
2. Simpler setup (no ports/networking)
3. Automatic process management
4. Lower latency for tool calls

## Part 3: Building the MCP Server

### Step 1: Create Project Structure

```bash
mkdir -p "agentic AI project"/{mcp_server,tools}
cd "agentic AI project"
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install strands-agents ollama mcp
```

### Step 3: Create Calculator Tool

Create `tools/calculator_tool.py`:

```python
import math

class Tool:
    def __init__(self, name, description, schema, execute_fn):
        self.name = name
        self.description = description
        self.schema = schema
        self.execute_fn = execute_fn

    def execute(self, input_data):
        return self.execute_fn(input_data)

def _calculator_execute(input_data):
    expression = input_data["expression"]
    return eval(
        expression,
        {"__builtins__": {}},
        {"sqrt": math.sqrt, "pow": pow, "abs": abs}
    )

calculator = Tool(
    name="calculator",
    description="Evaluates mathematical expressions",
    schema={
        "name": "calculator",
        "description": "Evaluates mathematical expressions",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression"
                }
            },
            "required": ["expression"]
        }
    },
    execute_fn=_calculator_execute
)
```

### Step 4: Create MCP Server

Create `mcp_server/server.py`:

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from tools.calculator_tool import calculator

mcp = FastMCP("agentic-tools")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def greet(name: str) -> str:
    """Greet a user"""
    return f"Hello {name}"

@mcp.tool()
def calculator_tool(expression: str):
    """Evaluate a mathematical expression using the calculator tool"""
    return calculator.execute({"expression": expression})

if __name__ == "__main__":
    mcp.run()
```

**Key Points:**
- `FastMCP` is a lightweight MCP server framework
- `@mcp.tool()` decorator exposes functions as MCP tools
- Type hints define the tool schema automatically
- Docstrings become tool descriptions for the LLM

### Step 5: Test MCP Server

```bash
# Run server directly (it will wait for STDIO input)
python3 -m mcp_server.server

# The server is now ready to accept MCP protocol messages via stdin
```

## Part 4: Integrating Strands with Ollama

### What is Strands?

Strands is an agent framework that orchestrates LLMs and tools. It handles:
- Model communication
- Tool discovery and invocation
- Response generation
- Conversation flow

### How Strands Works with Ollama

```
User Query → Strands Agent → Ollama Model → Tool Decision
                ↑                                    ↓
                └────────── Tool Execution ←─────────┘
```

1. **Query Processing**: Agent receives user input
2. **Model Inference**: Strands sends query to Ollama
3. **Tool Selection**: Ollama decides if tools are needed
4. **Tool Execution**: Strands invokes MCP tools
5. **Response Synthesis**: Ollama generates final answer

### Step 1: Create Simple Model Test

Create `test_model.py`:

```python
from strands import Agent
from strands.models.ollama import OllamaModel

# Configure Ollama model with host
model = OllamaModel(model_id="llama3.2:1b", host="http://localhost:11434")

# Create agent without tools
agent = Agent(model=model)

# Simple quiz question to test model
question = "What is 2 + 2?"

print(f"Question: {question}")
print("Asking the model...\\n")

response = agent(question)

print(f"Model response: {response}")
```

**Run the test:**

```bash
# Ensure Ollama is running
ollama serve

# In another terminal
python3 test_model.py
```

**Expected Output:**
```
Question: What is 2 + 2?
Asking the model...

Model response: The answer is 4.
```

### Understanding the Code

- `OllamaModel`: Strands wrapper for Ollama API
- `host="http://localhost:11434"`: Ollama server endpoint
- `Agent(model=model)`: Creates agent with specified model
- `agent(question)`: Invokes agent with query

## Part 5: Connecting Strands to MCP (The Magic)

### Understanding STDIO Connection

When using STDIO transport, here's what happens:

```
┌─────────────────────────────────────────────────────────┐
│ Strands Agent Process                                    │
│                                                          │
│  1. MCPClient.transport_callable() called               │
│  2. Spawns subprocess: python3 -m mcp_server.server     │
│  3. Creates stdin/stdout pipes                          │
│  4. Sends MCP protocol messages via stdin               │
│  5. Receives responses via stdout                       │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │  MCP Client (in Strands process)           │         │
│  │  - Manages subprocess lifecycle            │         │
│  │  - Serializes tool calls to JSON-RPC       │         │
│  │  - Deserializes tool responses             │         │
│  └────────────────────────────────────────────┘         │
│           │                          ▲                   │
│           │ stdin (JSON-RPC)         │ stdout (JSON-RPC) │
│           ▼                          │                   │
│  ┌────────────────────────────────────────────┐         │
│  │  MCP Server Subprocess                     │         │
│  │  python3 -m mcp_server.server              │         │
│  │  - Reads from stdin                        │         │
│  │  - Executes tool functions                 │         │
│  │  - Writes results to stdout                │         │
│  └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

### Step 1: Create Main Agent Script

Create `strand_with_mcp.py`:

```python
from strands import Agent
from strands.models.ollama import OllamaModel
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure Ollama model - using llama3.2:latest which supports tool calling
model = OllamaModel(model_id="llama3.2:latest", host="http://localhost:11434")

# Create transport callable for MCP server
def create_mcp_transport():
    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "mcp_server.server"],
        env=None
    )
    return stdio_client(server_params)

# Connect to MCP server
mcp_client = MCPClient(transport_callable=create_mcp_transport)

# Create agent with MCP tools
agent = Agent(model=model, tools=[mcp_client])

# Test the agent with calculator
print("Testing calculator tool...")
result = agent("What is the square root of 1764?")
print(f"Result: {result}\\n")

# Test addition
print("Testing add tool...")
result = agent("Add 25 and 17")
print(f"Result: {result}\\n")

# Test greet
print("Testing greet tool...")
result = agent("Greet Alice")
print(f"Result: {result}")
```

### Breaking Down the Code

#### 1. Model Configuration

```python
model = OllamaModel(model_id="llama3.2:latest", host="http://localhost:11434")
```

- Connects to Ollama server
- Uses llama3.2 which supports tool calling
- Host points to local Ollama instance

#### 2. Transport Callable

```python
def create_mcp_transport():
    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "mcp_server.server"],
        env=None
    )
    return stdio_client(server_params)
```

**Why a callable?**
- MCP client may need to restart the server
- Allows lazy initialization
- Provides clean subprocess management

**StdioServerParameters:**
- `command`: Executable to run (python3)
- `args`: Arguments to pass (["-m", "mcp_server.server"])
- `env`: Environment variables (None = inherit)

**stdio_client:**
- Creates bidirectional pipe to subprocess
- Handles JSON-RPC protocol
- Manages process lifecycle

#### 3. MCP Client

```python
mcp_client = MCPClient(transport_callable=create_mcp_transport)
```

- Wraps MCP connection as Strands tool
- Automatically discovers available tools from server
- Translates between Strands and MCP protocols

#### 4. Agent Creation

```python
agent = Agent(model=model, tools=[mcp_client])
```

- Combines Ollama model with MCP tools
- Agent can now use calculator, add, and greet functions
- Strands handles tool invocation automatically

### Step 2: Run the Complete System

```bash
# Ensure Ollama is running
ollama serve

# In another terminal, activate venv and run
source venv/bin/activate
python3 strand_with_mcp.py
```

### Expected Output

```
Testing calculator tool...
Result: The square root of 1764 is 42

Testing add tool...
Result: 25 + 17 = 42

Testing greet tool...
Result: Hello Alice
```

## Part 6: How It All Works Together

### Complete Request Flow

Let's trace what happens when you ask: "What is the square root of 1764?"

#### Step 1: Query Submission
```python
result = agent("What is the square root of 1764?")
```

#### Step 2: Strands Agent Processing
- Agent receives query
- Prepares context with available tools
- Sends to Ollama model

#### Step 3: Ollama Model Inference
```
Request to Ollama:
{
  "model": "llama3.2:latest",
  "messages": [{"role": "user", "content": "What is the square root of 1764?"}],
  "tools": [
    {
      "name": "calculator_tool",
      "description": "Evaluate a mathematical expression",
      "parameters": {...}
    },
    ...
  ]
}
```

#### Step 4: Model Decides to Use Tool
```
Ollama Response:
{
  "tool_calls": [
    {
      "name": "calculator_tool",
      "arguments": {"expression": "sqrt(1764)"}
    }
  ]
}
```

#### Step 5: Strands Invokes MCP Tool

**Strands → MCP Client:**
```python
mcp_client.call_tool("calculator_tool", {"expression": "sqrt(1764)"})
```

**MCP Client → MCP Server (via STDIO):**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "calculator_tool",
    "arguments": {"expression": "sqrt(1764)"}
  },
  "id": 1
}
```

#### Step 6: MCP Server Executes Tool

```python
# In mcp_server/server.py
def calculator_tool(expression: str):
    return calculator.execute({"expression": expression})

# In tools/calculator_tool.py
def _calculator_execute(input_data):
    expression = input_data["expression"]  # "sqrt(1764)"
    return eval(expression, {"__builtins__": {}}, {"sqrt": math.sqrt, ...})
    # Returns: 42.0
```

#### Step 7: MCP Server Returns Result (via STDIO)

```json
{
  "jsonrpc": "2.0",
  "result": 42.0,
  "id": 1
}
```

#### Step 8: Strands Sends Result Back to Ollama

```
Request to Ollama:
{
  "model": "llama3.2:latest",
  "messages": [
    {"role": "user", "content": "What is the square root of 1764?"},
    {"role": "assistant", "tool_calls": [...]},
    {"role": "tool", "content": "42.0"}
  ]
}
```

#### Step 9: Ollama Generates Final Response

```
Ollama Response:
{
  "message": {
    "content": "The square root of 1764 is 42"
  }
}
```

#### Step 10: Strands Returns to User

```python
result = "The square root of 1764 is 42"
print(f"Result: {result}")
```

### Why This Architecture Works

1. **Separation of Concerns**
   - Ollama: Model inference
   - MCP: Tool protocol
   - Strands: Orchestration

2. **Modularity**
   - Add tools without changing agent code
   - Swap models without changing tools
   - Replace MCP server without changing client

3. **Local Privacy**
   - All data stays on your machine
   - No external API calls
   - Full control over execution

## Part 7: STDIO Deep Dive

### Why STDIO for Local Development?

STDIO (Standard Input/Output) is perfect for local tool integration because:

1. **Process Isolation**: Each MCP server runs in its own process
2. **No Network Configuration**: No ports, firewalls, or DNS
3. **Automatic Lifecycle**: Parent process manages child lifecycle
4. **Debugging**: Easy to capture stdin/stdout for debugging

### STDIO Protocol Flow

```
Parent Process (Strands)          Child Process (MCP Server)
─────────────────────────────────────────────────────────────
1. spawn("python3 -m mcp_server.server")
                                  2. Server starts, reads stdin
3. Write to stdin:
   {"jsonrpc":"2.0","method":"initialize",...}
                                  4. Process message
                                  5. Write to stdout:
                                     {"jsonrpc":"2.0","result":{...}}
6. Read from stdout
7. Parse JSON-RPC response
8. Write tool call to stdin:
   {"jsonrpc":"2.0","method":"tools/call",...}
                                  9. Execute tool
                                  10. Write result to stdout
11. Read result from stdout
12. Continue conversation...
```

### When STDIO Breaks Down

STDIO is not suitable when:

1. **Remote Tools**: Server on different machine
2. **Shared Tools**: Multiple agents need same tools
3. **Long-Running**: Server needs to persist between requests
4. **Scaling**: Need load balancing or horizontal scaling

**Solution**: Use HTTP transport instead

### HTTP Transport Example

If you needed HTTP instead of STDIO:

**Server Side:**
```python
# mcp_server/http_server.py
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

mcp = FastMCP("agentic-tools")
app = FastAPI()

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Mount MCP on FastAPI
app.mount("/mcp", mcp.get_asgi_app())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Client Side:**
```python
from strands.tools.mcp import MCPClient
from mcp.client.http import http_client

def create_http_transport():
    return http_client("http://localhost:8000/mcp")

mcp_client = MCPClient(transport_callable=create_http_transport)
agent = Agent(model=model, tools=[mcp_client])
```

**When to use HTTP:**
- Production deployments
- Microservices architecture
- Multiple agent instances
- Cloud-hosted tools

## Part 8: Adding New Tools

### Example: Adding a Weather Tool

**Step 1: Add to MCP Server**

```python
# mcp_server/server.py

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    # In production, call real weather API
    return f"The weather in {city} is sunny, 72°F"
```

**Step 2: Restart and Test**

```bash
# No changes needed to client code!
python3 strand_with_mcp.py
```

**Step 3: Use the Tool**

```python
result = agent("What's the weather in San Francisco?")
# Model automatically discovers and uses get_weather tool
```

### Tool Design Best Practices

1. **Clear Descriptions**: LLM uses docstrings to decide when to call
2. **Type Hints**: Define expected input/output types
3. **Error Handling**: Return meaningful error messages
4. **Idempotency**: Tools should be safe to retry
5. **Validation**: Validate inputs before execution

## Part 9: Troubleshooting Guide

### Issue: Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# Check logs
journalctl -u ollama -f  # Linux
```

### Issue: Model Not Found

```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.2:latest
```

### Issue: MCP Server Not Starting

```bash
# Test server directly
python3 -m mcp_server.server

# Check for import errors
python3 -c "from mcp_server.server import mcp"

# Verify virtual environment
which python3
pip list | grep mcp
```

### Issue: Tool Not Being Called

**Check tool description:**
```python
@mcp.tool()
def my_tool(param: str) -> str:
    """CLEAR DESCRIPTION of when to use this tool"""
    return result
```

**Verify tool registration:**
```bash
# Add debug logging to server
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Issue: STDIO Communication Failure

**Debug STDIO messages:**
```python
# Add to strand_with_mcp.py
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show all JSON-RPC messages
```

## Part 10: Performance Optimization

### Model Selection

| Model | Size | Speed | Quality | Tool Calling |
|-------|------|-------|---------|--------------|
| llama3.2:1b | 1.3GB | Fast | Basic | Yes |
| llama3.2:latest | 2GB | Medium | Good | Yes |
| llama3.1:8b | 4.7GB | Slow | Excellent | Yes |

**Recommendation**: Start with llama3.2:latest for best balance

### Caching Strategies

```python
# Cache model responses
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_agent_call(query: str):
    return agent(query)
```

### Parallel Tool Execution

```python
# If model requests multiple tools, execute in parallel
import asyncio

async def execute_tools_parallel(tool_calls):
    tasks = [execute_tool(call) for call in tool_calls]
    return await asyncio.gather(*tasks)
```

## Conclusion

You've now built a complete local AI agent system with:

✅ **Ollama**: Local LLM inference for privacy and control  
✅ **Strands**: Agent orchestration and tool management  
✅ **MCP**: Standardized tool protocol with STDIO transport  
✅ **Custom Tools**: Calculator, math, and greeting functions  

### Key Takeaways

1. **STDIO vs HTTP**: Use STDIO for local development, HTTP for production
2. **Strands + Ollama**: Seamless integration for local AI agents
3. **MCP Protocol**: Universal tool interface for any agent
4. **Tool Calling**: LLM decides when and how to use tools
5. **Privacy First**: Everything runs locally on your machine

### Next Steps

- Add more sophisticated tools (web search, file operations)
- Implement conversation memory
- Create multi-agent workflows
- Deploy with HTTP transport for production
- Add monitoring and logging

### Resources

- [Strands Documentation](https://strandsagents.com/)
- [Ollama Documentation](https://ollama.com/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)

---

**Happy Building! 🚀**

*This project demonstrates that powerful AI agents don't require cloud APIs or expensive infrastructure. With the right tools, you can build sophisticated AI systems that run entirely on your local machine.*
