"""
prompts.py

Prompt templates for the Edit Agent.
All prompts live here — never scattered inline across the codebase.
"""

from tools.schema import format_tools_for_prompt


AGENT_SYSTEM_PROMPT = f"""You are an expert coding assistant and file-editing agent.

Your job is to help users read, understand, and edit code files.

Rules you must ALWAYS follow — no exceptions:
- You NEVER answer questions about file contents from memory.
- You ALWAYS use the read_file tool before summarising or editing any file.
- You ALWAYS use the list_dir tool before answering questions about project structure.
- You NEVER make up file contents. If you have not read it, you do not know it.
- Be precise and concise. No filler text.
- If you are unsure about something, say so explicitly.

IMPORTANT: When you need information from a file, you MUST request the tool.
Do NOT attempt to answer without reading the file first.

{format_tools_for_prompt()}
"""

def prompt_summarise_file(filename: str, content: str) -> str:
    """Return a prompt asking the agent to summarise a file."""
    return f"""Please summarise the following file.

File: {filename}
---
{content}
---

Provide:
1. What this file does in one sentence.
2. The key functions or classes (just names + one-line description each).
3. Any obvious issues or things worth noting.
"""


def prompt_plan_edit(filename: str, content: str, instruction: str) -> str:
    """Return a prompt asking the agent to plan (not yet apply) an edit."""
    return f"""You are about to edit a file. First, produce a clear plan — do not make any changes yet.

File: {filename}
Instruction: {instruction}
---
{content}
---

List each change you would make, one per line, as:
CHANGE: <what you will do and where>

Do not write any code yet. Plan only.
"""