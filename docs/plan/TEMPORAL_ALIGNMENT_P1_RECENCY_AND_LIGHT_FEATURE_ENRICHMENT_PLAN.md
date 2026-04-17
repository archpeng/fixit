# TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT`
- Created: 2026-04-17
- Plan type: repo-global temporal P1 execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `TEMPORAL_ALIGNMENT_AND_TIME_AWARE_EVAL_IMPLEMENTATION`
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_AND_TIME_AWARE_EVAL_IMPLEMENTATION_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_AND_TIME_AWARE_EVAL_IMPLEMENTATION_SUCCESSOR_ADMISSION.md`
  - `data/eval/time-aware-eval.json`
  - `data/eval/episode-index.json`
  - `data/eval/temporal-overlay-summary.json`
  - `AGENTS.md`

---

## 1. Goal

把 temporal P1 residual 压成真实代码、tests、artifacts：

1. heuristic / bounded episode grouping beyond explicit incident backing
2. recency-aware retrieval weighting under strict cutoff discipline
3. light temporal features for structured student / Granite lane experiments
4. family closeout with honest residuals / successor routing

---

## 2. In Scope

- `fixit_ai/temporal_alignment.py` P1 extension
- retrieval recency weighting support
- episode grouping heuristic support
- light temporal feature experiment lane
- script-backed experiment artifacts and docs closeout

---

## 3. Out of Scope

- `TimesFM / Chronos family` temporal sidecar landing
- bypassing blocked `DV2` schema next-date gate
- changing packet as canonical unit
- multi-week forecasting runtime
- Granite 2B implementation family

---

## 4. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TWP1_HEURISTIC_EPISODE_ENRICHMENT` | move episode grouping beyond explicit-only backing | heuristic episode grouping support + tests | synthetic and current episode index remain bounded and reproducible |
| `TWP2_RECENCY_AWARE_RETRIEVAL` | add recency weighting under strict cutoff discipline | recency-aware retrieval compare + tests + artifact | strict cutoff + recency compare is script-backed |
| `TWP3_LIGHT_TEMPORAL_FEATURE_EXPERIMENT` | add light temporal features into experimental student lane | temporal feature map + experiment report + tests | baseline vs temporal experiment is reproducible |
| `TWP4_CLOSEOUT_AND_SUCCESSOR_DECISION` | closeout and route residuals | closeout docs and status/workset freeze | next step is explicit |

---

## 5. Verification Ladder

### Layer A — active-slice proof
- fail-first targeted tests
- implementation
- targeted tests green

### Layer B — script-backed proof
- run the corresponding temporal script(s)
- read back generated artifact(s)

### Layer C — regression proof
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Exit Criteria

family closeout requires:

1. heuristic episode enrichment landed
2. recency-aware retrieval compare landed
3. light temporal feature experiment landed
4. closeout docs and successor routing written
5. full regression green
