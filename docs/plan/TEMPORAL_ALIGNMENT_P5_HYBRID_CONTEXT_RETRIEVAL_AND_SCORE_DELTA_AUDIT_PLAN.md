# TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT`
- Created: 2026-04-17
- Plan type: repo-global temporal P5 execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION`
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION_SUCCESSOR_ADMISSION.md`
  - `data/eval/temporal-episode-context-probe.json`
  - `AGENTS.md`

---

## 1. Goal

把 temporal P4 residual 压成真实代码、tests、artifacts：

1. build a bounded hybrid retrieval lane that fuses raw packet priors and episode-context priors
2. audit score deltas between raw-only and hybrid retrieval under anti-leakage discipline
3. quantify where hybrid fusion changes retrieval confidence / top-hit routing without faking metric lift
4. close family honestly with successor routing

---

## 2. In Scope

- `fixit_ai/temporal_alignment.py` P5 extension
- hybrid raw/context retrieval fusion
- score-delta audit artifact
- script-backed json/md outputs
- closeout docs and successor routing

---

## 3. Out of Scope

- bypassing blocked `DV2` schema gate
- pretending P5 already proves production metric lift
- temporal sidecar production landing
- replacing packet as canonical decision unit
- fabricating exact timestamps from coarse text hints

---

## 4. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TP5W1_HYBRID_CONTEXT_RETRIEVAL_FUSION` | build hybrid fusion of raw priors and episode-context priors | hybrid retrieval builder + tests | fusion is bounded, explainable, and reproducible |
| `TP5W2_SCORE_DELTA_AUDIT` | quantify hybrid-vs-raw score deltas and top-hit changes | hybrid probe artifact + markdown + tests | compare is reproducible and honest |
| `TP5W3_CLOSEOUT_AND_SUCCESSOR_DECISION` | close family and route residuals | closeout docs + status/workset freeze | next step is explicit |

---

## 5. Verification Ladder

### Layer A — active-slice proof
- fail-first targeted tests
- implementation
- targeted tests green

### Layer B — script-backed proof
- run `python3 scripts/run_temporal_hybrid_context_probe.py`
- read back generated artifacts

### Layer C — regression proof
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Exit Criteria

family closeout requires:

1. hybrid retrieval fusion landed
2. score-delta audit landed
3. artifacts are refreshed and readable
4. closeout docs and successor routing written
5. full regression green
