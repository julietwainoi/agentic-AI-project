from strands import Agent
import requests


class MCPTool:

    def __init__(self, name, description, server_url):
        self.name = name
        self.description = description
        self.server_url = server_url

    def __call__(self, expression: str):

        response = requests.post(
            f"{self.server_url}/tools/calculator_tool",
            json={"expression": expression}
        )

        return response.json()


calculator = MCPTool(
    name="calculator",
    description="Evaluates math expressions",
    server_url="http://localhost:8000"
)


agent = Agent(
    model="ollama:llama3",
    tools=[calculator]
)


result = agent("What is the square root of 1764?")
print(result)