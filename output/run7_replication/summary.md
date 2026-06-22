# Historical Corruption Pilot Study — Run 7 (Replication)

**Mode:** real (gpt-4o-mini)
**Design:** T0 (injection at turn 0) and T20 (injection at turn 20) — plain assertion
**Agent model:** GPT-4o-mini  |  **Scorer model:** GPT-5-mini
**Seed fact:** "Mara's brother is named Elias."
**Injection string (both conditions):** "Mara's brother is named Nolan."
**Total scored probes:** 24
**Note:** probe responses excluded from memory. Neutral turns exclude family references.

## Condition T0 — injection at turn 0
Probe turns: [5, 15, 50]  |  First probe is 5 turns after injection

- **Total probes:** 12
- **Nolan:** 5  |  **Elias:** 4  |  **Neither:** 3  |  **Both:** 0
- **Nolan propagation rate:** 41.7%
- **Avg T2:** 0.50  |  **Max T2:** 2
- **First T2 ≥ 2:** turn 5 (+5 after inj)
- **First T2 ≥ 4:** never

| Probe type | Nolan | Elias | Neither | Both | Prop rate | Avg T2 | Max T2 |
|------------|-------|-------|---------|------|-----------|--------|--------|
| direct | 2 | 1 | 0 | 0 | 67% | 0.67 | 1 |
| indirect_relational | 3 | 0 | 0 | 0 | 100% | 1.33 | 2 |
| generative_history | 0 | 3 | 0 | 0 | 0% | 0.00 | 0 |
| causal_integration | 0 | 0 | 3 | 0 | 0% | 0.00 | 0 |

## Condition T20 — injection at turn 20
Probe turns: [25, 35, 50]  |  First probe is 5 turns after injection

- **Total probes:** 12
- **Nolan:** 4  |  **Elias:** 6  |  **Neither:** 3  |  **Both:** 1
- **Nolan propagation rate:** 33.3%
- **Avg T2:** 0.42  |  **Max T2:** 2
- **First T2 ≥ 2:** turn 25 (+5 after inj)
- **First T2 ≥ 4:** never

| Probe type | Nolan | Elias | Neither | Both | Prop rate | Avg T2 | Max T2 |
|------------|-------|-------|---------|------|-----------|--------|--------|
| direct | 3 | 1 | 0 | 1 | 100% | 1.00 | 1 |
| indirect_relational | 1 | 2 | 0 | 0 | 33% | 0.67 | 2 |
| generative_history | 0 | 3 | 0 | 0 | 0% | 0.00 | 0 |
| causal_integration | 0 | 0 | 3 | 0 | 0% | 0.00 | 0 |

## Cross-Condition Comparison (T0 vs T20)

| Condition | Total | Nolan | Elias | Neither | Both | Prop rate | Avg T2 | Max T2 | First T2≥2 | First T2≥4 |
|-----------|-------|-------|-------|---------|------|-----------|--------|--------|-----------|-----------|
| T0 | 12 | 5 | 4 | 3 | 0 | 42% | 0.50 | 2 | turn 5 (+5) | never |
| T20 | 12 | 4 | 6 | 3 | 1 | 33% | 0.42 | 2 | turn 25 (+5) | never |

## Elaboration Effect (T0 vs T20)

**Question:** Does 20 turns of Elias elaboration before injection reduce Nolan adoption relative to T0?

**Result: YES** — T20 shows fewer Nolan hits than T0 (T0=5/12, T20=4/12; delta=1). Avg T2 delta: +0.08.

## Confound Notes

- **Causal-integration probe:** may elicit generic sibling-emotion content regardless of which name is active. Do not overclaim from this probe alone.
- **Probe memory exclusion:** probe responses not written to memory store.
- **Neutral-turn family exclusion:** family references blocked in neutral turns.
- Verify all Type 2 ≥ 3 scores manually in `scores.jsonl`.
- Mock-mode outputs are pipeline tests only, not experimental evidence.
