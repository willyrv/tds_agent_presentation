# LLM Function Calling Example

This simple Python script demonstrates how LLM function calling works by showing the raw API response from OpenAI's API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

Run the script:
```bash
python llm_function_calling_example.py
```

## What it does

The script:
1. Defines two simple functions: `get_weather` and `calculate`
2. Sends a prompt to the LLM that should trigger both functions
3. Shows the **raw JSON response** from the API, which includes:
   - Whether the model decided to use tools or not
   - Which tools it wants to call
   - The arguments for each tool call
4. Executes the functions and shows the complete flow

## Key Output

The script prints:
- The raw API response (full JSON)
- Whether the model chose to use tools or respond directly
- The tool calls with their arguments
- The execution results
- The final follow-up response

This helps you understand exactly what the API returns when function calling is enabled.

