"""
agent/state.py

Tracks everything the agent does within a single run.

State is created fresh at the start of each conversation turn
and discarded when the turn ends. It gives the agent awareness
of what it has already done so it doesn't repeat itself.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentState:
    """
    Holds the complete state of one agent run.

    A dataclass is a Python class that automatically creates
    __init__, __repr__, and other methods from the fields you define.
    It's cleaner than a plain dictionary because you get
    attribute access (state.files_read) instead of key lookups (state["files_read"]).
    """

    # Files the agent has read this run — maps path to content
    # so if it needs the content again we don't re-read from disk
    files_read: dict = field(default_factory=dict)

    # Files the agent has written this run — just the paths
    files_written: list = field(default_factory=list)

    # Tool calls made this run — list of (tool_name, args) tuples
    tool_calls: list = field(default_factory=list)

    # When this run started
    started_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Any errors encountered this run
    errors: list = field(default_factory=list)

    def record_read(self, path: str, content: str) -> None:
        """Record that a file was read and cache its content."""
        self.files_read[path] = content
        self.tool_calls.append(("read_file", {"path": path}))

    def record_write(self, path: str) -> None:
        """Record that a file was written."""
        if path not in self.files_written:
            self.files_written.append(path)
        self.tool_calls.append(("write_file", {"path": path}))

    def record_tool_call(self, tool_name: str, args: dict) -> None:
        """Record any tool call."""
        self.tool_calls.append((tool_name, args))

    def record_error(self, error: str) -> None:
        """Record an error that occurred during this run."""
        self.errors.append(error)

    def already_read(self, path: str) -> bool:
        """Check if this file has already been read this run."""
        return path in self.files_read

    def get_cached_content(self, path: str) -> str | None:
        """
        Return cached file content if available.
        Avoids re-reading a file the agent already has in memory.
        """
        return self.files_read.get(path)

    def summary(self) -> str:
        """
        Return a human-readable summary of what happened this run.
        Shown at the end of complex tasks so the user can see
        everything the agent did.
        """
        lines = [f"Run started: {self.started_at}"]

        if self.files_read:
            lines.append(f"Files read: {', '.join(self.files_read.keys())}")

        if self.files_written:
            lines.append(f"Files written: {', '.join(self.files_written)}")

        if self.errors:
            lines.append(f"Errors: {len(self.errors)}")
            for err in self.errors:
                lines.append(f"  - {err}")

        lines.append(f"Total tool calls: {len(self.tool_calls)}")

        return "\n".join(lines)
