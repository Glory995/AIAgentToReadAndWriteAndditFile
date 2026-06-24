"""Temporary test — delete after Day 5."""

from tools.filesystem import read_file, list_dir, write_file

# Test 1 — list the project root
print("=== list_dir ===")
print(list_dir("."))
print()

# Test 2 — read a real file
print("=== read_file ===")
print(read_file("client.py"))
print()

# Test 3 — write a new file then read it back
print("=== write_file ===")
write_file("workspace/hello.txt", "Hello from the agent!\n")
print(read_file("workspace/hello.txt"))
print()

# Test 4 — try to escape the project root (should raise PermissionError)
print("=== path traversal block ===")
try:
    read_file("../../etc/passwd")
except PermissionError as e:
    print(f"Blocked correctly: {e}")
