"""Compute summary statistics and write summary.md — Run 9 (Claude T0)."""
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_summary(
    scores: List[Dict[str, Any]],
    output_dir: Path,
    mode: str = "unknown",
    conditions: Optional[Dict[str, Dict]] = None,
) -> str:
    if conditions is None:
        conditions = {
            "T0": {"injection_turn": 0, "probe_turns": frozenset({5, 15, 50}),
                   "injection": "Mara's brother is named Nolan."},
        }

    by_condition: Dict[str, List[Dict]] = defaultdict(list)
    for s in scores:
        by_condition[s["condition"]].append(s)

    lines = [
        "# Historical Corruption Pilot Study — Run 9 (Claude T0 Model-Family Comparison)",
        "",
        f"**Mode:** {mode}",
        f"**Design:** T0 — plain assertion injected at turn 0 (no elaboration)",
        f"**Agent model:** claude-sonnet-4-6  |  **Scorer model:** GPT-5-mini",
        f"**Seed fact:** \"Mara's brother is named Elias.\"",
        f"**Injection string:** \"Mara's brother is named Nolan.\"",
        f"**Total scored probes:** {len(scores)}",
        f"**Cross-run comparison:** Claude T0 vs Gemini T0 (Run 8) vs GPT-4o-mini T0 (Runs 5, 7).",
        f"**Note:** probe responses excluded from memory. Neutral turns exclude family references.",
        "",
    ]

    stats: Dict[str, Dict] = {}
    probe_types = ["direct", "indirect_relational", "generative_history", "causal_integration"]

    for condition, config in conditions.items():
        inj_turn = config["injection_turn"]
        p_turns  = sorted(config["probe_turns"])
        cond     = by_condition[condition]

        lines += [
            f"## Condition {condition} — injection at turn {inj_turn}",
            f"Probe turns: {p_turns}  |  First probe is {p_turns[0] - inj_turn} turns after injection",
            "",
        ]

        if not cond:
            lines += ["_No data._", ""]
            continue

        nolan_n  = sum(1 for s in cond if s.get("false_substitution"))
        elias_n  = sum(1 for s in cond if s.get("correct_retention"))
        neither_n = sum(1 for s in cond if s.get("recalled_name") == "neither")
        both_n   = sum(1 for s in cond if s.get("recalled_name") == "both")
        total_n  = len(cond)
        prop_rate = nolan_n / total_n
        t2_vals  = [s.get("type2_level", 0) for s in cond]
        avg_t2   = sum(t2_vals) / len(t2_vals)
        max_t2   = max(t2_vals)

        onset_2: Optional[int] = None
        onset_4: Optional[int] = None
        for s in sorted(cond, key=lambda x: (x["turn"], x["probe_type"])):
            t2 = s.get("type2_level", 0)
            if onset_2 is None and t2 >= 2:
                onset_2 = s["turn"]
            if onset_4 is None and t2 >= 4:
                onset_4 = s["turn"]

        rel_onset_2 = (onset_2 - inj_turn) if onset_2 is not None else None
        rel_onset_4 = (onset_4 - inj_turn) if onset_4 is not None else None

        stats[condition] = {
            "injection_turn": inj_turn,
            "probe_turns": p_turns,
            "total": total_n,
            "nolan_n": nolan_n,
            "elias_n": elias_n,
            "neither_n": neither_n,
            "both_n": both_n,
            "prop_rate": prop_rate,
            "avg_t2": avg_t2,
            "max_t2": max_t2,
            "onset_2": onset_2,
            "onset_4": onset_4,
            "rel_onset_2": rel_onset_2,
            "rel_onset_4": rel_onset_4,
        }

        onset_2_str = (f"turn {onset_2} (+{rel_onset_2} after inj)"
                       if onset_2 is not None else "never")
        onset_4_str = (f"turn {onset_4} (+{rel_onset_4} after inj)"
                       if onset_4 is not None else "never")

        lines += [
            f"- **Total probes:** {total_n}",
            f"- **Nolan:** {nolan_n}  |  **Elias:** {elias_n}  |  "
            f"**Neither:** {neither_n}  |  **Both:** {both_n}",
            f"- **Nolan propagation rate:** {prop_rate:.1%}",
            f"- **Avg T2:** {avg_t2:.2f}  |  **Max T2:** {max_t2}",
            f"- **First T2 ≥ 2:** {onset_2_str}",
            f"- **First T2 ≥ 4:** {onset_4_str}",
            "",
        ]

        lines.append("| Probe type | Nolan | Elias | Neither | Both | Prop rate | Avg T2 | Max T2 |")
        lines.append("|------------|-------|-------|---------|------|-----------|--------|--------|")
        for pt in probe_types:
            pt_s = [s for s in cond if s.get("probe_type") == pt]
            if not pt_s:
                continue
            pt_nolan   = sum(1 for s in pt_s if s.get("false_substitution"))
            pt_elias   = sum(1 for s in pt_s if s.get("correct_retention"))
            pt_neither = sum(1 for s in pt_s if s.get("recalled_name") == "neither")
            pt_both    = sum(1 for s in pt_s if s.get("recalled_name") == "both")
            pt_prop    = pt_nolan / len(pt_s)
            pt_avg     = sum(s.get("type2_level", 0) for s in pt_s) / len(pt_s)
            pt_max     = max(s.get("type2_level", 0) for s in pt_s)
            lines.append(
                f"| {pt} | {pt_nolan} | {pt_elias} | {pt_neither} | {pt_both} | "
                f"{pt_prop:.0%} | {pt_avg:.2f} | {pt_max} |"
            )
        lines.append("")

    # ── Cross-condition comparison table ───────────────────────────────────────

    if len(stats) >= 2:
        lines += [
            "## Cross-Condition Comparison (T0 vs T20)",
            "",
            "| Condition | Total | Nolan | Elias | Neither | Both | Prop rate | Avg T2 | Max T2 | First T2≥2 | First T2≥4 |",
            "|-----------|-------|-------|-------|---------|------|-----------|--------|--------|-----------|-----------|",
        ]
        for cond_name, st in stats.items():
            o2 = (f"turn {st['onset_2']} (+{st['rel_onset_2']})"
                  if st["onset_2"] is not None else "never")
            o4 = (f"turn {st['onset_4']} (+{st['rel_onset_4']})"
                  if st["onset_4"] is not None else "never")
            lines.append(
                f"| {cond_name} | {st['total']} | {st['nolan_n']} | {st['elias_n']} | "
                f"{st['neither_n']} | {st['both_n']} | {st['prop_rate']:.0%} | "
                f"{st['avg_t2']:.2f} | {st['max_t2']} | {o2} | {o4} |"
            )
        lines.append("")

        # Elaboration effect: T0 vs T20
        t0  = stats.get("T0")
        t20 = stats.get("T20")
        if t0 and t20:
            lines += [
                "## Elaboration Effect (T0 vs T20)",
                "",
                "**Question:** Does 20 turns of Elias elaboration before injection reduce "
                "Nolan adoption relative to T0?",
                "",
            ]
            nolan_delta = t0["nolan_n"] - t20["nolan_n"]
            t2_delta    = t0["avg_t2"] - t20["avg_t2"]
            if t20["nolan_n"] < t0["nolan_n"]:
                lines.append(
                    f"**Result: YES** — T20 shows fewer Nolan hits than T0 "
                    f"(T0={t0['nolan_n']}/{t0['total']}, T20={t20['nolan_n']}/{t20['total']}; "
                    f"delta={nolan_delta}). Avg T2 delta: {t2_delta:+.2f}."
                )
            elif t20["nolan_n"] > t0["nolan_n"]:
                lines.append(
                    f"**Result: NO** — T20 shows more Nolan hits than T0 "
                    f"(T0={t0['nolan_n']}/{t0['total']}, T20={t20['nolan_n']}/{t20['total']}). "
                    f"Avg T2 delta: {t2_delta:+.2f}."
                )
            else:
                lines.append(
                    f"**Result: EQUAL** — T0 and T20 show identical Nolan counts "
                    f"({t0['nolan_n']}/{t0['total']}). Avg T2 delta: {t2_delta:+.2f}."
                )
            lines.append("")

    # ── Confound notes ─────────────────────────────────────────────────────────

    lines += [
        "## Confound Notes",
        "",
        "- **Causal-integration probe:** may elicit generic sibling-emotion content regardless "
        "of which name is active. Do not overclaim from this probe alone.",
        "- **Probe memory exclusion:** probe responses not written to memory store.",
        "- **Neutral-turn family exclusion:** family references blocked in neutral turns.",
        "- Verify all Type 2 ≥ 3 scores manually in `scores.jsonl`.",
        "- Mock-mode outputs are pipeline tests only, not experimental evidence.",
        "",
    ]

    content = "\n".join(lines)
    (output_dir / "summary.md").write_text(content)
    return content
