from strands import Agent
from strands.models.ollama import OllamaModel
from tools.calculator_tool import calculator

# Configure Ollama model
model = OllamaModel(model_name="llama3.2")

# Create agent with calculator tool
agent = Agent(model=model, tools=[calculator])

# Run the agent
result = agent("What is the square root of 1764?")
print(result)
