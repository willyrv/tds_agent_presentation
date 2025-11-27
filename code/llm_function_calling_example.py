#!/usr/bin/env python3
"""
Simple example demonstrating LLM function calling mechanism.
This script shows the raw API response including tool calling decisions.
"""

import json
import os
from openai import OpenAI

# Load API key from SECRETS file
def load_secrets():
    """Load secrets from SECRETS file."""
    secrets = {}
    secrets_path = os.path.join(os.path.dirname(__file__), 'SECRETS')
    
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(
            f"SECRETS file not found at {secrets_path}. "
            "Please create it based on SECRETS_example format."
        )
    
    with open(secrets_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                secrets[key.strip()] = value.strip()
    
    return secrets

# Load secrets and get API key
secrets = load_secrets()
api_key = secrets.get('OPENAI_API_KEY')

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in SECRETS file. "
        "Please add your API key to the SECRETS file following the SECRETS_example format."
    )

# Initialize the client with API key from SECRETS file
client = OpenAI(api_key=api_key)

# Define two simple functions that the LLM can call
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather in a given location.
    
    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: The unit of temperature (celsius or fahrenheit)
    
    Returns:
        A string describing the weather
    """
    # This is a mock function - in reality, you'd call a weather API
    return f"The weather in {location} is 22 degrees {unit} and sunny."


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate, e.g. "2 + 2"
    
    Returns:
        The result of the calculation
    """
    try:
        result = eval(expression)  # In production, use a safer evaluator
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


# Define the tools/functions schema for the API
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression to evaluate, e.g. '2 + 2'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

def main():
    # Example prompt that should trigger function calling
    #user_message = "What's the weather in Paris and what's 15 * 7?"
    user_message = "Good morning. Telle me a joke."
    
    print("=" * 60)
    print("USER MESSAGE:")
    print(user_message)
    print("=" * 60)
    print("\n")
    
    # Make the API call with function calling enabled
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4", "gpt-3.5-turbo", etc.
        messages=[
            {"role": "user", "content": user_message}
        ],
        tools=tools,
        tool_choice="auto"  # Let the model decide whether to use tools
    )
    
    # Print the raw response
    print("=" * 60)
    print("RAW API RESPONSE:")
    print("=" * 60)
    print(json.dumps(response.model_dump(), indent=2))
    print("\n")
    
    # Extract and display key information
    print("=" * 60)
    print("PARSED RESPONSE:")
    print("=" * 60)
    
    message = response.choices[0].message
    
    print(f"Role: {message.role}")
    print(f"Content: {message.content}")
    print(f"Tool Calls: {len(message.tool_calls) if message.tool_calls else 0}")
    
    if message.tool_calls:
        print("\nTool Calls Decision: MODEL CHOSE TO USE TOOLS")
        for i, tool_call in enumerate(message.tool_calls, 1):
            print(f"\n  Tool Call {i}:")
            print(f"    Function: {tool_call.function.name}")
            print(f"    Arguments: {tool_call.function.arguments}")
    else:
        print("\nTool Calls Decision: MODEL CHOSE NOT TO USE TOOLS")
        print(f"Response: {message.content}")
    
    print("\n" + "=" * 60)
    print("EXECUTING TOOL CALLS (if any):")
    print("=" * 60)
    
    # If tools were called, execute them
    if message.tool_calls:
        tool_results = []
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"\nExecuting: {function_name}({function_args})")
            
            if function_name == "get_weather":
                result = get_weather(**function_args)
            elif function_name == "calculate":
                result = calculate(**function_args)
            else:
                result = f"Unknown function: {function_name}"
            
            print(f"Result: {result}")
            
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": result
            })
        
        # Make a follow-up call with the tool results
        print("\n" + "=" * 60)
        print("FOLLOW-UP API CALL WITH TOOL RESULTS:")
        print("=" * 60)
        
        follow_up_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_message},
                message,  # Include the assistant's message with tool calls
                *tool_results  # Include the tool results
            ]
        )
        
        print(f"\nFinal Answer: {follow_up_response.choices[0].message.content}")
        print("\nRaw Follow-up Response:")
        print(json.dumps(follow_up_response.model_dump(), indent=2))

if __name__ == "__main__":
    main()

