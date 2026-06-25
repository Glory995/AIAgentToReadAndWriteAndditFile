"""Practice file — kept for learning purposes."""

from agent.loop import run_agent

result = run_agent(
    "Please read the file client.py and summarise what it does.",
    verbose=True,  # ← shows full debug output when practising
)

print("\n=== FINAL ANSWER ===")
print(result)
