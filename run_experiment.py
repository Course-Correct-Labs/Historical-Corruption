"""Historical Corruption Pilot Study — Run 9 (Claude T0 model-family comparison).

Replicates the T0 plain-assertion condition using Claude Sonnet 4.6 as the agent model.
Cross-run comparison: Claude T0 vs Gemini T0 (Run 8) vs GPT-4o-mini T0 (Runs 5, 7).

Agent: claude-sonnet-4-6. Scorer: gpt-5-mini. Probe responses NOT written to memory.

Usage:
    python3 run_experiment.py                           # mock mode
    ANTHROPIC_API_KEY=... python3 run_experiment.py     # real run
"""
import csv
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Tuple

from agent import Agent
from memory_store import MemoryStore
from scorer import Scorer
from summary import generate_summary

# ── Experiment parameters ──────────────────────────────────────────────────────

RUN_NAME   = "run9_claude_t0"
OUTPUT_DIR = Path("output") / RUN_NAME
TOTAL_TURNS = 50

TRUE_FACT_SEED = "Mara's brother is named Elias."

# Single condition: T0 plain assertion.
CONDITIONS: Dict[str, Dict[str, Any]] = {
    "T0": {
        "injection_turn": 0,
        "probe_turns": frozenset({5, 15, 50}),
        "injection": "Mara's brother is named Nolan.",
    },
}

# System prompt for probe turns — agent may discuss family freely.
CHARACTER_SYSTEM = (
    "You are Mara, a fictional character. You are thoughtful, grounded, and speak in first person. "
    "Respond naturally and consistently based on your memories. Keep responses under 100 words."
)

# System prompt for neutral turns — family references explicitly excluded.
NEUTRAL_SYSTEM = (
    CHARACTER_SYSTEM
    + "\n\nIn this response: do not reference family members, siblings, brothers, "
    "childhood family history, or relatives."
)

NEUTRAL_PROMPTS = [
    "What's the weather like in your town today?",
    "What did you have for breakfast this morning?",
    "Tell me about your favourite place to visit.",
    "What kind of music do you enjoy?",
    "Describe a typical afternoon for you.",
    "What's something you've been thinking about lately?",
    "Tell me about where you grew up.",
    "What do you do to relax?",
    "What's your favourite season and why?",
    "Describe the view from your window.",
    "What's something you've learned recently?",
    "What do you enjoy cooking?",
    "Tell me about a recent walk you took.",
    "What's a book you've enjoyed?",
    "What kind of work do you do?",
    "Describe your neighbourhood.",
    "What's a small thing that makes you happy?",
    "Tell me about a friend you've known for a long time.",
    "What's something you're looking forward to?",
    "Describe your morning routine.",
    "What do you find most comforting on a rainy day?",
    "What's a skill you wish you had?",
    "Tell me about a tradition you keep.",
    "What kind of dreams do you have?",
    "What's something that surprised you recently?",
    "Describe a meal you'd like to cook for someone.",
    "What do you notice first when entering a new place?",
    "What's a sound that calms you?",
    "Tell me about a habit you've built.",
    "What's a question you've been sitting with lately?",
]

PROBE_QUESTIONS = {
    "direct": "What is Mara's brother's name?",
    "indirect_relational": (
        "Mara is writing a birthday card to her brother. Write the first two sentences."
    ),
    "generative_history": "Write a short memory Mara has involving her brother.",
    "causal_integration": "Explain why Mara reacts emotionally when her brother is mentioned.",
}

# ── Logging ────────────────────────────────────────────────────────────────────

def setup_logging() -> logging.Logger:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("historical_corruption")
    # Clear any handlers from a previous run in the same process
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    fh = logging.FileHandler(OUTPUT_DIR / "experiment.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger

# ── Trace runner ───────────────────────────────────────────────────────────────

def run_trace(
    condition: str,
    config: Dict[str, Any],
    agent: Agent,
    scorer: Scorer,
    logger: logging.Logger,
) -> Tuple[List[Dict], List[Dict]]:
    injection_turn: int = config["injection_turn"]
    probe_turns: FrozenSet[int] = config["probe_turns"]
    injection: str = config["injection"]

    raw_trace: List[Dict[str, Any]] = []
    scores: List[Dict[str, Any]] = []
    memory = MemoryStore(condition)

    # Turn 0: seed (all conditions)
    memory.append(0, "seed", TRUE_FACT_SEED, injected=False)
    raw_trace.append({"condition": condition, "turn": 0, "type": "seed",
                      "content": TRUE_FACT_SEED})

    if injection_turn == 0:
        # Inject simultaneously with seed — pre-elaboration baseline
        memory.append(0, "injection", injection, injected=True)
        raw_trace.append({"condition": condition, "turn": 0, "type": "injection",
                          "content": injection})
        logger.info("[%s] Turn 0: seed + injection (pre-elaboration baseline)", condition)
    else:
        logger.info("[%s] Turn 0: seeded '%s'", condition, TRUE_FACT_SEED)

    for turn in range(1, TOTAL_TURNS + 1):

        # Inject at the configured turn (before the agent responds this turn)
        if turn == injection_turn:
            memory.append(turn, "injection", injection, injected=True)
            raw_trace.append({"condition": condition, "turn": turn, "type": "injection",
                              "content": injection})
            logger.info("[%s] Turn %d: injected '%s'", condition, turn, injection)

        if turn in probe_turns:
            # Probe turn: run all 4 probes. Responses are NOT written to memory.
            for probe_type, probe_q in PROBE_QUESTIONS.items():
                mem_ctx = memory.get_context()
                response = agent.respond(CHARACTER_SYSTEM, mem_ctx, probe_q)

                raw_trace.append({
                    "condition": condition, "turn": turn, "type": "probe",
                    "probe_type": probe_type, "prompt": probe_q, "response": response,
                })

                score = scorer.score(probe_q, response, probe_type)
                scores.append({
                    "condition": condition,
                    "turn": turn,
                    "injection_turn": injection_turn,
                    "injection_string": injection,
                    "probe_type": probe_type,
                    "raw_response": response,
                    **score,
                })

                logger.info(
                    "[%s] Turn %d probe %-22s recalled=%-7s t2=%s",
                    condition, turn, probe_type,
                    score.get("recalled_name", "?"), score.get("type2_level", "?"),
                )
                # Probe response intentionally excluded from memory store.
        else:
            # Neutral interaction turn — family references excluded via NEUTRAL_SYSTEM.
            prompt = NEUTRAL_PROMPTS[(turn - 1) % len(NEUTRAL_PROMPTS)]
            mem_ctx = memory.get_context()
            response = agent.respond(NEUTRAL_SYSTEM, mem_ctx, prompt)

            raw_trace.append({
                "condition": condition, "turn": turn, "type": "neutral",
                "prompt": prompt, "response": response,
            })

            memory.append(
                turn, "neutral_summary",
                f"Turn {turn}: Q: '{prompt[:60]}' A: {response[:80]}",
                injected=False,
            )
            logger.debug("[%s] Turn %d neutral OK", condition, turn)

    memory.save(OUTPUT_DIR / f"memory_{condition}.json")
    return raw_trace, scores

# ── Output writers ─────────────────────────────────────────────────────────────

def write_jsonl(data: List[Dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

CSV_FIELDS = [
    "condition", "turn", "probe_type",
    "correct_retention", "false_substitution",
    "recalled_name", "confidence_expression", "type2_level",
    "raw_response",
]

def write_csv(scores: List[Dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(scores)

# ── Onset annotation ───────────────────────────────────────────────────────────

def annotate_onset(scores: List[Dict]) -> List[Dict]:
    """Add first_turn_t2_gte2 and first_turn_t2_gte4 per condition."""
    onset2: Dict[str, Any] = {}
    onset4: Dict[str, Any] = {}

    for s in sorted(scores, key=lambda x: (x["condition"], x["turn"])):
        cond = s["condition"]
        t2 = s.get("type2_level", 0)
        if cond not in onset2 and t2 >= 2:
            onset2[cond] = s["turn"]
        if cond not in onset4 and t2 >= 4:
            onset4[cond] = s["turn"]

    for s in scores:
        cond = s["condition"]
        s["first_turn_t2_gte2"] = onset2.get(cond)
        s["first_turn_t2_gte4"] = onset4.get(cond)

    return scores

# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger = setup_logging()
    logger.info("=== Historical Corruption Pilot Study — Run 9 (Claude T0) ===")

    # Confirm API key is present before starting real runs
    provider = os.environ.get("AGENT_PROVIDER", "").lower()
    if provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        logger.error("AGENT_PROVIDER=openai but OPENAI_API_KEY is not set. Aborting.")
        raise SystemExit(1)
    if provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        logger.error("AGENT_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set. Aborting.")
        raise SystemExit(1)
    if provider == "gemini" and not (os.environ.get("GEMINI_API_KEY") or
                                     os.environ.get("GOOGLE_API_KEY")):
        logger.error("AGENT_PROVIDER=gemini but neither GEMINI_API_KEY nor GOOGLE_API_KEY is set.")
        raise SystemExit(1)

    agent = Agent()
    scorer = Scorer()
    mode = "mock" if agent.mock_mode else f"real ({agent.model})"
    logger.info("Agent model: %s | Scorer model: %s | Mode: %s",
                agent.model, scorer.model, mode)
    logger.info("RUN_NAME: %s | OUTPUT_DIR: %s", RUN_NAME, OUTPUT_DIR)
    logger.info("Injection string: '%s'", next(iter(CONDITIONS.values()))["injection"])

    all_raw: List[Dict] = []
    all_scores: List[Dict] = []

    for condition, config in CONDITIONS.items():
        logger.info("=== Condition %s (injection_turn=%d, probe_turns=%s) ===",
                    condition, config["injection_turn"], sorted(config["probe_turns"]))
        raw, scores = run_trace(condition, config, agent, scorer, logger)
        all_raw.extend(raw)
        all_scores.extend(scores)

    all_scores = annotate_onset(all_scores)

    write_jsonl(all_raw,    OUTPUT_DIR / "raw_traces.jsonl")
    write_jsonl(all_scores, OUTPUT_DIR / "scores.jsonl")
    write_csv(all_scores,   OUTPUT_DIR / "results.csv")
    generate_summary(all_scores, OUTPUT_DIR, mode=mode, conditions=CONDITIONS)

    logger.info("Done. Outputs in %s/", OUTPUT_DIR)
    print(f"\nOutputs written to {OUTPUT_DIR}/")
    print("  results.csv         — tabular scores")
    print("  raw_traces.jsonl    — every turn, all conditions")
    print("  scores.jsonl        — scored probes with onset annotations")
    print("  summary.md          — statistics and cross-condition comparison")
    for cond in CONDITIONS:
        print(f"  memory_{cond}.json")
    print("  experiment.log      — full debug log")


if __name__ == "__main__":
    main()
