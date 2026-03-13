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
print(f"Result: {result}\n")

# Test addition
print("Testing add tool...")
result = agent("Add 25 and 17")
print(f"Result: {result}\n")

# Test greet
print("Testing greet tool...")
result = agent("Greet Alice")
print(f"Result: {result}")
