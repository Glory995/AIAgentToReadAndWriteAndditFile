"""
main.py

Entry point for the Edit Agent.

Usage:
    python main.py

The agent will prompt you for a task, then work through it
using the available tools — reading, listing, and writing files.
"""

import os
import requests
from dotenv import load_dotenv

from tools.parser import extract_tool_request
from tools.filesystem import read_file, list_dir, write_file
from prompts import AGENT_SYSTEM_PROMPT

from tools.sandbox import ensure_sandbox_exists

# Make sure the sandbox exists before the agent tries to use it
ensure_sandbox_exists()

load_dotenv()

# Maps tool names to actual Python functions
TOOL_REGISTRY = {
    "read_file": read_file,
    "list_dir": list_dir,
    "write_file": write_file,
}

MAX_ITERATIONS = 10


def run_tool(tool_request: dict) -> str:
    """Execute the tool the model requested and return the result."""
    tool_name = tool_request["tool"]
    args = tool_request["args"]

    if tool_name not in TOOL_REGISTRY:
        return f"Error: unknown tool '{tool_name}'."

    try:
        return str(TOOL_REGISTRY[tool_name](**args))
    except (TypeError, FileNotFoundError, PermissionError) as e:
        return f"Error calling '{tool_name}': {e}"


def call_model(messages: list) -> str:
    """Send the full conversation history to the model and return its reply."""
    url = f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/chat"
    model = os.getenv("DEFAULT_MODEL", "llama3.2")

    response = requests.post(
        url,
        json={"model": model, "stream": False, "messages": messages},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def main():
    print("=" * 55)
    print("  EDIT AGENT — Agentic AI Project")
    print("  Week 1 Milestone: Read-Only Agent")
    print("=" * 55)
    print()
    print("Available tools: read_file, list_dir, write_file")
    print("Type 'quit' to exit.")
    print()

    # Conversation history lives here — persists across ALL your messages
    # so the agent remembers the full conversation, not just one turn
    history = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # Add the user's message to the shared history
        history.append({"role": "user", "content": user_input})

        # Run the agent loop — passes the full history every iteration
        for iteration in range(1, MAX_ITERATIONS + 1):
            raw_response = call_model(history)
            tool_request = extract_tool_request(raw_response)

            if tool_request is None:
                # No tool needed — final answer
                # Add it to history so the next message has full context
                history.append({"role": "assistant", "content": raw_response})
                print()
                print(f"Agent: {raw_response}")
                print()
                break

            # Tool requested — run it and feed the result back
            tool_name = tool_request["tool"]
            print(f"  → using {tool_name}...")
            tool_result = run_tool(tool_request)

            # Both the tool request and result go into history
            history.append({"role": "assistant", "content": raw_response})
            history.append({"role": "user", "content": f"Tool result:\n{tool_result}"})

        else:
            print("Agent: reached maximum iterations.")


if __name__ == "__main__":
    main()
