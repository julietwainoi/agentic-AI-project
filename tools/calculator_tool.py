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
        {
            "sqrt": math.sqrt,
            "pow": pow,
            "abs": abs
        }
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