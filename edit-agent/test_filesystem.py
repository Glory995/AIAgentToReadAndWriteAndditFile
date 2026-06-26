"""Temporary test — delete after Day 5."""

from tools.filesystem import read_file, list_dir, write_file

# Test 1 — list the project root
print("=== list_dir ===")
print(list_dir("."))
print()

# Test 2 — read a real file
print("=== read_file ===")
print(read_file("sample_project/calculator.py"))
print()

# Test 3 — write a new file then read it back
print("=== write_file ===")
write_file("hello.txt", "Hello from the agent!\n")
print(read_file("hello.txt"))
print()

# Test 4 — try to escape the project root (should raise PermissionError)
print("=== path traversal block ===")
try:
    read_file("../../etc/passwd")
except PermissionError as e:
    print(f"Blocked correctly: {e}")



from tools.diff import generate_diff, has_changes

original = """def greet(name):
    print("hello " + name)
"""

proposed = """def greet(name):
    print(f"Hello, {name}!")
"""

print("=== generate_diff ===")
print(generate_diff(original, proposed, "greet.py"))

print("=== has_changes ===")
print(has_changes(original, proposed))  # should print True
print(has_changes(original, original))  # should print False


# ── Day 9 practice ──────────────────────────────────────
print("\n=== write_file with approval ===")
write_file("workspace/approval_test.txt", "This is a test file.\nLine two.\n")

# ── Day 10 practice ─────────────────────────────────────
from tools.sandbox import SANDBOX_DIR, safe_sandbox_path

print("\n=== sandbox ===")
print(f"Sandbox directory: {SANDBOX_DIR}")

# This should work — inside sandbox
print(safe_sandbox_path("sample_project/calculator.py"))

# This should be blocked — trying to escape
try:
    safe_sandbox_path("../../main.py")
except PermissionError as e:
    print(f"Blocked correctly: {e}")