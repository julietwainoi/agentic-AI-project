import re

class Agent:
    def __init__(self, tools=None):
        self.tools = tools or []
    
    def __call__(self, prompt):
        # Simple pattern matching for calculator
        if "square root" in prompt.lower():
            match = re.search(r'\d+', prompt)
            if match:
                num = match.group()
                result = self.tools[0].execute({"expression": f"sqrt({num})"})
                return f"The square root of {num} is {result}"
        
        return "I can help with calculations. Try asking about square roots or math expressions."
