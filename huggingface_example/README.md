# Hugging Face Tool Use Example

This example demonstrates how to use tool calling (function calling) with Hugging Face Transformers models.

Based on the official documentation: https://huggingface.co/docs/transformers/chat_extras

## Features

- Defines weather-related tools (temperature and wind speed)
- Loads a model that supports tool-use (Hermes-2-Pro-Llama-3-8B)
- Demonstrates the complete tool calling loop:
  1. Model generates a tool call request
  2. Tool is executed
  3. Tool result is fed back to the model
  4. Model generates a final response

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python tool_use_example.py
```

## Requirements

- Python 3.8+
- PyTorch (CPU or CUDA)
- Transformers library
- Accelerate library (for device_map="auto")

## Model

The script uses `NousResearch/Hermes-2-Pro-Llama-3-8B`, which is a 8B parameter model fine-tuned for tool use. The model will be automatically downloaded on first run.

## Notes

- The example uses simulated weather data
- Tool execution happens locally in the script
- The model generates tool calls in JSON format, which are parsed and executed
- The conversation loop handles tool calls and responses automatically

