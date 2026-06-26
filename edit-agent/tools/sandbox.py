"""
tools/sandbox.py

Defines and enforces the sandbox boundary for the agent.

The agent is only allowed to read and write files inside the
SANDBOX_DIR folder. Any attempt to access files outside this
boundary is blocked before it reaches the filesystem.

This protects your source code from accidental or malicious edits.
"""

import os

# The sandbox is the workspace/ folder inside the project root
# This is the ONLY place the agent is allowed to read or write
SANDBOX_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace")
)


def ensure_sandbox_exists() -> None:
    """
    Create the sandbox directory if it doesn't exist yet.
    Called once at startup so the agent always has somewhere to work.
    """
    os.makedirs(SANDBOX_DIR, exist_ok=True)


def safe_sandbox_path(path: str) -> str:
    """
    Resolve a path and verify it stays inside the sandbox.

    This is stricter than the project-root check in filesystem.py —
    it limits the agent to workspace/ only, not the whole project.

    Args:
        path: A relative path provided by the model.
              Can be relative to sandbox root (e.g. 'hello.txt')
              or include the workspace prefix (e.g. 'workspace/hello.txt')

    Returns:
        The resolved absolute path if it is inside the sandbox.

    Raises:
        PermissionError: If the path escapes the sandbox directory.
    """

    # Strip the 'workspace/' prefix if the model included it
    # so both 'hello.txt' and 'workspace/hello.txt' work correctly
    normalized = path.strip()
    if normalized.startswith("workspace/") or normalized.startswith("workspace\\"):
        normalized = normalized[len("workspace/") :]

    # Resolve to absolute path inside the sandbox
    resolved = os.path.abspath(os.path.join(SANDBOX_DIR, normalized))

    # The critical check — must stay inside sandbox
    if not resolved.startswith(SANDBOX_DIR):
        raise PermissionError(
            f"Access denied: '{path}' resolves outside the sandbox.\n"
            f"The agent can only access files inside 'workspace/'."
        )

    return resolved


def is_sandboxed_path(path: str) -> bool:
    """
    Quick check — is this path inside the sandbox?

    Args:
        path: Any file path to check.

    Returns:
        True if the path is inside the sandbox, False otherwise.
    """
    try:
        resolved = os.path.abspath(path)
        return resolved.startswith(SANDBOX_DIR)
    except Exception:
        return False


def sandbox_relative_path(absolute_path: str) -> str:
    """
    Convert an absolute sandbox path back to a relative display path.

    Example:
        /home/user/edit-agent/workspace/hello.txt
        → workspace/hello.txt

    Used when showing paths to the user so they see clean relative paths
    instead of long absolute paths.

    Args:
        absolute_path: An absolute path inside the sandbox.

    Returns:
        A clean relative path for display.
    """
    project_root = os.path.dirname(SANDBOX_DIR)
    return os.path.relpath(absolute_path, project_root)
