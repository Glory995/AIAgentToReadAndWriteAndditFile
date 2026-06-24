"""
tools/filesystem.py

Filesystem tools available to the agent.
Each function corresponds to a tool defined in tools/schema.py.

All paths are relative to the project root.
Path traversal outside the project root is blocked for safety.
"""

import os


# The root directory the agent is allowed to work inside.
# Every path gets resolved and checked against this.
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _safe_path(path: str) -> str:
    """
    Resolve a relative path and verify it stays inside PROJECT_ROOT.

    This blocks path traversal attacks — for example an instruction like
    read_file("../../etc/passwd") would escape the project folder without this check.

    Args:
        path: A relative path provided by the model.

    Returns:
        The resolved absolute path if it is safe.

    Raises:
        PermissionError: If the path escapes PROJECT_ROOT.
    """
    resolved = os.path.abspath(os.path.join(PROJECT_ROOT, path))

    if not resolved.startswith(PROJECT_ROOT):
        raise PermissionError(
            f"Access denied: '{path}' resolves outside the project root."
        )

    return resolved


def read_file(path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        path: Relative path to the file.

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the path escapes the project root.
    """
    safe = _safe_path(path)

    if not os.path.isfile(safe):
        raise FileNotFoundError(f"File not found: '{path}'")

    with open(safe, "r", encoding="utf-8") as f:
        return f.read()


def list_dir(path: str = ".") -> str:
    """
    List the files and folders inside a directory.

    Args:
        path: Relative path to the directory. Defaults to project root.

    Returns:
        A formatted string listing all entries in the directory.

    Raises:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If the path escapes the project root.
    """
    safe = _safe_path(path)

    if not os.path.isdir(safe):
        raise FileNotFoundError(f"Directory not found: '{path}'")

    entries = os.listdir(safe)

    if not entries:
        return f"Directory '{path}' is empty."

    # Separate folders and files, sort each alphabetically
    folders = sorted([e for e in entries if os.path.isdir(os.path.join(safe, e))])
    files = sorted([e for e in entries if os.path.isfile(os.path.join(safe, e))])

    lines = [f"Contents of '{path}':"]
    for folder in folders:
        lines.append(f"  [dir]  {folder}/")
    for file in files:
        lines.append(f"  [file] {file}")

    return "\n".join(lines)


def write_file(path: str, content: str) -> str:
    """
    Write content to a file, replacing whatever was there before.

    Args:
        path:    Relative path to the file to write.
        content: The full content to write.

    Returns:
        A confirmation message.

    Raises:
        PermissionError: If the path escapes the project root.
    """
    safe = _safe_path(path)

    # Create any missing parent directories automatically
    os.makedirs(os.path.dirname(safe), exist_ok=True)

    with open(safe, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Successfully wrote {len(content)} characters to '{path}'."
