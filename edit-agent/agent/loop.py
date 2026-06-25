"""
agent/loop.py

The core agent loop: think → act → observe → repeat.

The model is called repeatedly until it stops requesting tools
and produces a final plain text response.
"""

import os
import requests
from dotenv import load_dotenv

from tools.parser import extract_tool_request
from tools.filesystem import read_file, list_dir, write_file
from prompts import AGENT_SYSTEM_PROMPT

load_dotenv()

# Maps tool names (strings the model sends) to actual Python functions
TOOL_REGISTRY = {
    "read_file": read_file,
    "list_dir": list_dir,
    "write_file": write_file,
}

MAX_ITERATIONS = 10  # safety cap — prevents infinite loops


def run_tool(tool_request: dict) -> str:
    """
    Execute the tool the model requested.
    Returns the result as a string to feed back to the model.

    Args:
        tool_request: A dict with 'tool' and 'args' keys from the model.

    Returns:
        The tool's output as a plain string.
    """
    tool_name = tool_request["tool"]
    args = tool_request["args"]

    if tool_name not in TOOL_REGISTRY:
        return f"Error: unknown tool '{tool_name}'. Available: {list(TOOL_REGISTRY.keys())}"

    tool_fn = TOOL_REGISTRY[tool_name]

    try:
        result = tool_fn(**args)
        return str(result)
    except (TypeError, FileNotFoundError, PermissionError) as e:
        return f"Error calling tool '{tool_name}': {e}"


def run_agent(user_instruction: str, verbose: bool = False) -> str:
    """
    Run the agent loop for a given user instruction.

    Args:
        user_instruction: The task the user wants the agent to perform.
        verbose:          If True, print debug info each iteration.
                          If False, print only a clean progress indicator.

    Returns:
        The agent's final plain text response.
    """
    # The conversation history — grows each iteration so the model
    # always knows what has already happened in this session
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_instruction},
    ]

    url = f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/chat"
    model = os.getenv("DEFAULT_MODEL", "llama3.2")

    for iteration in range(1, MAX_ITERATIONS + 1):
        if verbose:
            print(f"[agent] Iteration {iteration}")

        # Call the model with the full conversation history
        payload = {
            "model": model,
            "stream": False,
            "messages": messages,
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        raw_response = response.json()["message"]["content"]

        if verbose:
            print(f"[agent] Model response: {raw_response}")

        # Try to find a tool request anywhere in the response
        tool_request = extract_tool_request(raw_response)

        if tool_request is None:
            # No tool request — this is the final answer
            if verbose:
                print("[agent] Task complete.")
            return raw_response

        # A tool was requested — run it and feed the result back
        tool_name = tool_request["tool"]

        if verbose:
            print(
                f"[agent] Running tool: {tool_name} with args: {tool_request['args']}"
            )
        else:
            # Clean single-line progress for normal use
            print(f"  → using {tool_name}...")

        tool_result = run_tool(tool_request)

        if verbose:
            print(f"[agent] Tool result: {tool_result}")

        # Append to conversation history so the model remembers
        messages.append({"role": "assistant", "content": raw_response})
        messages.append({"role": "user", "content": f"Tool result:\n{tool_result}"})

    return "Error: agent reached maximum iterations without completing the task."
