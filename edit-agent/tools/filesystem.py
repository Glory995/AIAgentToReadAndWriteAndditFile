"""
tools/filesystem.py

Filesystem tools available to the agent.
Each function corresponds to a tool defined in tools/schema.py.

All paths are sandboxed to the workspace/ directory.
The agent cannot read or write outside this boundary.
"""

import os
from tools.sandbox import safe_sandbox_path, SANDBOX_DIR


def read_file(path: str) -> str:
    """
    Read and return the contents of a file inside the sandbox.

    Args:
        path: Path to the file, relative to workspace/.

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the path escapes the sandbox.
    """
    safe = safe_sandbox_path(path)

    if not os.path.isfile(safe):
        raise FileNotFoundError(
            f"File not found: '{path}'. "
            f"Remember the agent can only access files inside workspace/."
        )

    with open(safe, "r", encoding="utf-8") as f:
        return f.read()


def list_dir(path: str = ".") -> str:
    """
    List the files and folders inside a sandbox directory.

    Args:
        path: Path to list, relative to workspace/. Defaults to workspace/ root.

    Returns:
        A formatted string listing all entries.

    Raises:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If the path escapes the sandbox.
    """
    safe = safe_sandbox_path(path)

    if not os.path.isdir(safe):
        raise FileNotFoundError(f"Directory not found: '{path}' inside workspace/.")

    entries = os.listdir(safe)

    if not entries:
        return f"workspace/{path} is empty."

    folders = sorted([e for e in entries if os.path.isdir(os.path.join(safe, e))])
    files = sorted([e for e in entries if os.path.isfile(os.path.join(safe, e))])

    lines = [f"Contents of 'workspace/{path}':"]
    for folder in folders:
        lines.append(f"  [dir]  {folder}/")
    for file in files:
        lines.append(f"  [file] {file}")

    return "\n".join(lines)


def write_file(path: str, content: str) -> str:
    """
    Propose a file edit inside the sandbox and write only if approved.

    Args:
        path:    Path to the file, relative to workspace/.
        content: The full content to write.

    Returns:
        A message describing what happened.

    Raises:
        PermissionError: If the path escapes the sandbox.
    """
    # Safety check runs first — always
    safe = safe_sandbox_path(path)

    from agent.approval import request_approval_or_skip

    approved, message = request_approval_or_skip(path, content)

    if approved:
        os.makedirs(os.path.dirname(safe), exist_ok=True)
        with open(safe, "w", encoding="utf-8") as f:
            f.write(content)

    return message
