"""Temporary test """
from client import complete
from prompts import AGENT_SYSTEM_PROMPT, prompt_summarise_file

fake_file_content = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b
"""

user_prompt = prompt_summarise_file("fake file content ", fake_file_content)
response = complete(AGENT_SYSTEM_PROMPT, user_prompt)
print(response)