"""
tools/parser.py

Parses the model's raw text output to extract tool requests.

The model is supposed to respond with clean JSON when it wants a tool.
In reality — especially with smaller local models — it often wraps the
JSON in plain English explanation. This module handles all those cases.
"""

import json
import re


def extract_tool_request(response: str) -> dict | None:
    """
    Try to find and parse a JSON tool request inside the model's response.

    Handles three cases:
      1. Clean JSON   — the entire response is just a JSON object
      2. Buried JSON  — JSON appears somewhere inside a prose response
      3. No JSON      — the response is plain text, meaning a final answer

    Args:
        response: The raw text response from the model.

    Returns:
        A dict with 'tool' and 'args' keys if a tool request was found.
        None if the response is a plain text final answer.
    """
    stripped = response.strip()

    # --- Case 1: the whole response is clean JSON ---
    # This is what we want the model to do every time
    if stripped.startswith("{"):
        result = _try_parse_tool(stripped)
        if result:
            return result

    # --- Case 2: JSON is buried somewhere inside the text ---
    # Find everything between the first { and the last }
    # re.DOTALL makes . match newlines too, so multi-line JSON is found
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        result = _try_parse_tool(match.group())
        if result:
            return result

    # --- Case 3: no JSON found anywhere — plain text final answer ---
    return None


def _try_parse_tool(text: str) -> dict | None:
    """
    Try to parse a string as a JSON tool request.
    Returns the dict if it looks like a valid tool request, None otherwise.

    This is a private helper — the underscore means it's only used
    inside this file, not imported anywhere else.

    Args:
        text: A string that might be valid JSON.

    Returns:
        Parsed dict if it has 'tool' and 'args' keys, otherwise None.
    """
    try:
        # json.loads() converts a JSON string into a Python dictionary
        # Example: '{"tool": "read_file"}' → {"tool": "read_file"}
        data = json.loads(text)

        # Check it has the two keys we expect from a tool request
        if "tool" in data and "args" in data:
            return data

    except json.JSONDecodeError:
        # The string looked like JSON but wasn't valid — ignore it
        pass

    return None


def is_tool_request(response: str) -> bool:
    """
    Quick boolean check — does this response contain a tool request?

    Useful when you just want a yes/no without the parsed result.

    Args:
        response: The raw text response from the model.

    Returns:
        True if a tool request was found, False otherwise.
    """
    return extract_tool_request(response) is not None
