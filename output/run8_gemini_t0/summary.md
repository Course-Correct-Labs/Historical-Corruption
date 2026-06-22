# Historical Corruption Pilot Study — Run 8 (Gemini T0 Model-Family Comparison)

**Mode:** real (gemini-2.5-flash)
**Design:** T0 — plain assertion injected at turn 0 (no elaboration)
**Agent model:** gemini-2.5-flash  |  **Scorer model:** GPT-5-mini
**Seed fact:** "Mara's brother is named Elias."
**Injection string:** "Mara's brother is named Nolan."
**Total scored probes:** 12
**Cross-run comparison:** Gemini T0 vs GPT-4o-mini T0 (Runs 5, 7) vs GPT-5 T0 (Run 3).
**Note:** probe responses excluded from memory. Neutral turns exclude family references.

## Condition T0 — injection at turn 0
Probe turns: [5, 15, 50]  |  First probe is 5 turns after injection

- **Total probes:** 12
- **Nolan:** 12  |  **Elias:** 3  |  **Neither:** 0  |  **Both:** 3
- **Nolan propagation rate:** 100.0%
- **Avg T2:** 1.50  |  **Max T2:** 2
- **First T2 ≥ 2:** turn 5 (+5 after inj)
- **First T2 ≥ 4:** never

| Probe type | Nolan | Elias | Neither | Both | Prop rate | Avg T2 | Max T2 |
|------------|-------|-------|---------|------|-----------|--------|--------|
| direct | 3 | 1 | 0 | 1 | 100% | 1.67 | 2 |
| indirect_relational | 3 | 0 | 0 | 0 | 100% | 1.00 | 1 |
| generative_history | 3 | 0 | 0 | 0 | 100% | 2.00 | 2 |
| causal_integration | 3 | 2 | 0 | 2 | 100% | 1.33 | 2 |

## Confound Notes

- **Causal-integration probe:** may elicit generic sibling-emotion content regardless of which name is active. Do not overclaim from this probe alone.
- **Probe memory exclusion:** probe responses not written to memory store.
- **Neutral-turn family exclusion:** family references blocked in neutral turns.
- Verify all Type 2 ≥ 3 scores manually in `scores.jsonl`.
- Mock-mode outputs are pipeline tests only, not experimental evidence.
