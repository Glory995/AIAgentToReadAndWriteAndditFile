"""
tools/schema.py

Defines the tools available to the agent.
Each tool has a name, description, and a list of required arguments.

The model reads these definitions and uses them to request actions.
The actual implementation of each tool lives in tools/filesystem.py (Day 5).
"""

# Each tool is a dictionary describing:
#   name        — what the model uses to request this tool
#   description — plain English explanation of what it does
#   args        — the inputs the model must provide when requesting it

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "args": {
            "path": "The relative path to the file to read."
        }
    },
    {
        "name": "list_dir",
        "description": "List all files and folders inside a directory.",
        "args": {
            "path": "The relative path to the directory to list."
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file, replacing whatever was there before.",
        "args": {
            "path":    "The relative path to the file to write.",
            "content": "The full content to write to the file."
        }
    },
]


def format_tools_for_prompt() -> str:
    """
    Format the tool list as a readable block of text for injection into a prompt.
    The model reads this to know what tools are available and how to request them.
    """
    lines = ["You have access to the following tools:", ""]

    for tool in TOOLS:
        lines.append(f"Tool: {tool['name']}")
        lines.append(f"Description: {tool['description']}")
        lines.append("Arguments:")
        for arg_name, arg_desc in tool["args"].items():
            lines.append(f"  - {arg_name}: {arg_desc}")
        lines.append("")  # blank line between tools

    lines.append(
        "When you need to use a tool, respond with ONLY this JSON format, nothing else:\n"
        '{"tool": "<tool_name>", "args": {"<arg_name>": "<value>"}}\n'
        "If you do not need a tool, respond normally in plain text."
    )

    return "\n".join(lines)