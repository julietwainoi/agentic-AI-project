from strands import Agent
from strands.models.ollama import OllamaModel

# Configure Ollama model with host
model = OllamaModel(model_id="llama3.2:1b", host="http://localhost:11434")

# Create agent without tools
agent = Agent(model=model)

# Simple quiz question to test model
question = "What is 2 + 2?"

print(f"Question: {question}")
print("Asking the model...\n")

response = agent(question)

print(f"Model response: {response}")
