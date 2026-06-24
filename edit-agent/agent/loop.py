"""
agent/loop.py

The core agent loop: think → act → observe → repeat.

The model is called repeatedly until it stops requesting tools
and produces a final plain text response.
"""

from client import complete
from prompts import AGENT_SYSTEM_PROMPT
from tools.parser import extract_tool_request
from tools.filesystem import read_file, list_dir, write_file


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
        return f"Error: unknown tool '{tool_name}'. Available tools: {list(TOOL_REGISTRY.keys())}"

    # Look up the function in TOOL_REGISTRY and call it
    # **args unpacks the dictionary as keyword arguments
    # Example: if args = {"path": "client.py"}
    # then tool_fn(**args) becomes tool_fn(path="client.py")
    tool_fn = TOOL_REGISTRY[tool_name]

    try:
        result = tool_fn(**args)
        return str(result)
    except (TypeError, FileNotFoundError, PermissionError) as e:
        return f"Error calling tool '{tool_name}': {e}"


def run_agent(user_instruction: str) -> str:
    """
    Run the agent loop for a given user instruction.

    Keeps calling the model until it produces a final plain text answer
    or the iteration limit is reached.

    Args:
        user_instruction: The task the user wants the agent to perform.

    Returns:
        The agent's final plain text response.
    """
    print(f"\n[agent] Starting task: {user_instruction}")

    # The conversation history — this list grows each iteration
    # so the model always knows what has already happened
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_instruction},
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"[agent] Iteration {iteration}")

        # Build the payload and call the model directly here
        # (moved from _call_model helper for clarity)
        import os, requests
        from dotenv import load_dotenv

        load_dotenv()

        url = f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/chat"
        payload = {
            "model": os.getenv("DEFAULT_MODEL", "llama3.2"),
            "stream": False,
            "messages": messages,
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        raw_response = response.json()["message"]["content"]

        print(f"[agent] Model response: {raw_response}")

        # Try to find a tool request anywhere in the response
        tool_request = extract_tool_request(raw_response)

        if tool_request is None:
            # No tool request found — this is the final answer
            print("[agent] Task complete.")
            return raw_response

        # Run the tool and get the result
        tool_name = tool_request["tool"]
        print(f"[agent] Running tool: {tool_name} with args: {tool_request['args']}")
        tool_result = run_tool(tool_request)
        print(f"[agent] Tool result: {tool_result}")

        # Add what happened to the conversation history
        # so the model remembers it on the next iteration
        messages.append({"role": "assistant", "content": raw_response})
        messages.append({"role": "user", "content": f"Tool result:\n{tool_result}"})

    return "Error: agent reached maximum iterations without completing the task."
