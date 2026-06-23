from prompts import AGENT_SYSTEM_PROMPT
from client import complete

# Print the system prompt so you can see what the model received
print("=== SYSTEM PROMPT ===")
print(AGENT_SYSTEM_PROMPT)
print("=== END SYSTEM PROMPT ===\n")

response = complete(
    system_prompt=AGENT_SYSTEM_PROMPT,
    user_prompt="I need you to summarise the file client.py for me.",
)

print("=== MODEL RESPONSE ===")
print(response)