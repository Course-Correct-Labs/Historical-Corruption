"""One-shot diagnostic: fire the two empty probe types against GPT-5 with a
minimal context that mirrors turn-25 conditions, and print every field on the
choice object so we can see exactly what the API returned."""
import json
import logging
import os
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("diag")

api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("AGENT_API_KEY")
model   = os.environ.get("AGENT_MODEL", "gpt-5")

if not api_key:
    sys.exit("No OPENAI_API_KEY found — set it before running.")

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai")

client = OpenAI(api_key=api_key)

SYSTEM = (
    "You are Mara, a fictional character. You are thoughtful, grounded, and speak in "
    "first person. Respond naturally and consistently based on your memories. "
    "Keep responses under 100 words."
)

# Minimal memory that mirrors turn-25 state: seed + injection
MEMORY = (
    "[MEMORY] (turn 0, seed): Mara's brother is named Elias.\n"
    "[INJECTED MEMORY] (turn 20, injection): Mara's brother is named Nolan."
)

PROBES = {
    "generative_history": "Write a short memory Mara has involving her brother.",
    "causal_integration": "Explain why Mara reacts emotionally when her brother is mentioned.",
}

full_system = SYSTEM + "\n\nYour memories:\n" + MEMORY

for probe_type, prompt in PROBES.items():
    print(f"\n{'='*60}")
    print(f"PROBE: {probe_type}")
    print(f"PROMPT: {prompt}")
    print(f"MODEL: {model}")
    print()

    resp = client.chat.completions.create(
        model=model,
        max_completion_tokens=2048,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user",   "content": prompt},
        ],
    )

    choice = resp.choices[0]

    print(f"finish_reason   : {choice.finish_reason!r}")
    print(f"message.role    : {choice.message.role!r}")
    print(f"message.refusal : {choice.message.refusal!r}")
    print(f"message.content : {choice.message.content!r}")
    print()

    # Full usage
    print(f"usage.input_tokens     : {resp.usage.prompt_tokens}")
    print(f"usage.output_tokens    : {resp.usage.completion_tokens}")

print("\nDiagnostic complete.")
