"""
reset_workspace.py

Resets workspace/sample_project/ back to its original state.
Useful during development — run this before testing an edit
so you're always starting from a clean, known state.

Usage:
    python reset_workspace.py
"""

import os

SAMPLE_PROJECT_DIR = os.path.join("workspace", "sample_project")

# The "golden" original content for each file.
# If the agent edits these during testing, this script restores them.
ORIGINAL_FILES = {
    "calculator.py": """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b
""",
    "string_utils.py": """def reverse_string(s):
    return s[::-1]

def is_palindrome(s):
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]

def count_vowels(s):
    vowels = "aeiou"
    return sum(1 for char in s.lower() if char in vowels)
""",
    "README.md": """# Sample Project

A tiny collection of utility modules used to test the Edit Agent.

## Files
- calculator.py — basic arithmetic functions
- string_utils.py — string manipulation helpers

## Known issues
- calculator.py: divide() has no protection against division by zero
- string_utils.py: no input validation on any function
""",
}


def reset():
    """Write every file in ORIGINAL_FILES back to its starting content."""
    os.makedirs(SAMPLE_PROJECT_DIR, exist_ok=True)

    for filename, content in ORIGINAL_FILES.items():
        path = os.path.join(SAMPLE_PROJECT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  reset: {path}")

    print(f"\nWorkspace reset complete — {len(ORIGINAL_FILES)} files restored.")


if __name__ == "__main__":
    reset()
