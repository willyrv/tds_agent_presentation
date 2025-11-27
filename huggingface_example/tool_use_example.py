"""
Example script demonstrating tool-use with Hugging Face Transformers.

Based on: https://huggingface.co/docs/transformers/chat_extras

This script shows how to:
1. Define tools (functions) that the model can call
2. Pass tools to a chat model
3. Handle tool calls and responses in a conversation loop
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import re


def get_current_temperature(location: str, unit: str):
    """
    Get the current temperature at a location.

    Args:
        location: The location to get the temperature for, in the format "City, Country"
        unit: The unit to return the temperature in. (choices: ["celsius", "fahrenheit"])
    """
    # Simulated temperature data
    temperatures = {
        "Paris, France": {"celsius": 22, "fahrenheit": 72},
        "Toulouse, France": {"celsius": 25, "fahrenheit": 77},
        "New York, USA": {"celsius": 18, "fahrenheit": 64},
    }
    
    # Default values if location not found
    default_temp_c = 20
    default_temp_f = 68
    
    if location in temperatures:
        temp = temperatures[location][unit]
    else:
        temp = default_temp_c if unit == "celsius" else default_temp_f
    
    return float(temp)


def get_current_wind_speed(location: str):
    """
    Get the current wind speed in km/h at a given location.

    Args:
        location: The location to get the wind speed for, in the format "City, Country"
    """
    # Simulated wind speed data
    wind_speeds = {
        "Paris, France": 6.0,
        "Toulouse, France": 8.0,
        "New York, USA": 12.0,
    }
    
    return float(wind_speeds.get(location, 5.0))


def execute_tool_call(tool_call):
    """
    Execute a tool call and return the result as a string.
    
    Args:
        tool_call: Dictionary with 'name' and 'arguments' keys
        
    Returns:
        String representation of the tool result
    """
    tool_name = tool_call["name"]
    arguments = tool_call["arguments"]
    
    if tool_name == "get_current_temperature":
        result = get_current_temperature(
            location=arguments["location"],
            unit=arguments["unit"]
        )
        return str(result)
    elif tool_name == "get_current_wind_speed":
        result = get_current_wind_speed(
            location=arguments["location"]
        )
        return str(result)
    else:
        return f"Error: Unknown tool '{tool_name}'"


def main():
    print("=" * 60)
    print("Hugging Face Transformers - Tool Use Example")
    print("=" * 60)
    print()
    
    # Define tools
    tools = [get_current_temperature, get_current_wind_speed]
    print(f"✓ Defined {len(tools)} tools")
    print()
    
    # Load model and tokenizer
    print("Loading model and tokenizer...")
    checkpoint = "NousResearch/Hermes-2-Pro-Llama-3-8B"
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        model = AutoModelForCausalLM.from_pretrained(
            checkpoint,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        print(f"✓ Loaded model: {checkpoint}")
        print(f"✓ Device: {model.device}")
        print()
    except Exception as e:
        print(f"Error loading model: {e}")
        print("\nNote: You may need to install transformers and accelerate:")
        print("  pip install transformers accelerate")
        return
    
    # Initialize chat history
    messages = [
        {
            "role": "system",
            "content": "You are a bot that responds to weather queries. You should reply with the unit used in the queried location."
        },
        {
            "role": "user",
            "content": "Hey, what's the temperature in Paris right now? Please give me the temperature in Celsius."
        }
    ]
    
    print("Starting conversation...")
    print(f"User: {messages[-1]['content']}")
    print()
    
    # Conversation loop (handle up to 3 tool calls)
    max_iterations = 3
    for iteration in range(max_iterations):
        # Apply chat template with tools
        inputs = tokenizer.apply_chat_template(
            messages,
            tools=tools,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        )
        
        # Move inputs to model device
        inputs = {k: v.to(model.device) if isinstance(v, torch.Tensor) else v 
                 for k, v in inputs.items()}
        
        # Generate response
        print(f"[Iteration {iteration + 1}] Generating response...")
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True
        )
        
        # Decode only the new tokens
        response_text = tokenizer.decode(
            outputs[0][len(inputs["input_ids"][0]):],
            skip_special_tokens=True
        )
        
        print(f"Model output: {response_text}")
        print()
        
        # Try to parse tool call from response
        try:
            # Extract JSON from <tool_call> tags if present
            tool_call_match = re.search(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', response_text, re.DOTALL)
            if tool_call_match:
                json_str = tool_call_match.group(1)
            elif response_text.strip().startswith("{"):
                json_str = response_text.strip()
            else:
                json_str = None
            
            if json_str:
                tool_call_data = json.loads(json_str)
                
                if "name" in tool_call_data and "arguments" in tool_call_data:
                    # Model wants to call a tool
                    print(f"🔧 Tool call detected: {tool_call_data['name']}")
                    print(f"   Arguments: {tool_call_data['arguments']}")
                    
                    # Add tool call to messages
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [{
                            "type": "function",
                            "function": tool_call_data
                        }]
                    })
                    
                    # Execute tool
                    tool_result = execute_tool_call(tool_call_data)
                    print(f"   Result: {tool_result}")
                    print()
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "content": tool_result
                    })
                    
                    # Continue loop to let model process tool result
                    continue
        except json.JSONDecodeError:
            # Response is not a tool call, it's a final answer
            pass
        
        # If we get here, the model gave a final response
        print("=" * 60)
        print("Final Response:")
        print(response_text)
        print("=" * 60)
        break
    
    print("\n✓ Conversation complete!")


if __name__ == "__main__":
    main()

