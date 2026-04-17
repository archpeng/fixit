# TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE`
- Created: 2026-04-17
- Plan type: repo-global temporal P2 execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT`
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_SUCCESSOR_ADMISSION.md`
  - `data/eval/time-aware-eval.json`
  - `data/eval/temporal-feature-experiment.json`
  - `AGENTS.md`

---

## 1. Goal

把 temporal P1 的 remaining value-extraction gap 压成真实代码、tests、artifacts：

1. 在不伪造时间的前提下，扩展 exact-time historical prior surface
2. 用 strict cutoff discipline 对 expanded temporal prior pool 做 probe / compare
3. 判断 expanded exact-time priors 是否至少提升 strict history coverage / retrieval choice visibility
4. 以 honest closeout 结束 family，并写清 successor routing

---

## 2. In Scope

- `fixit_ai/temporal_alignment.py` P2 extension
- exact-time temporal prior catalog derived from packet-linked history
- strict-cutoff temporal prior probe and compare artifacts
- script-backed json/jsonl/md artifacts
- family closeout docs and successor routing

---

## 3. Out of Scope

- bypassing blocked `DV2` schema gate
- fabricating new dates or pretending coarse month hints are exact timestamps
- packet canonical-unit replacement
- temporal sidecar production landing
- long-sequence temporal backbone runtime

---

## 4. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TP2W1_EXACT_TIME_TEMPORAL_PRIOR_CATALOG` | derive richer exact-time prior rows from packet-linked history | prior catalog + summary + tests | catalog is bounded, packet-linked, and script-backed |
| `TP2W2_STRICT_CUTOFF_TEMPORAL_PRIOR_PROBE` | compare baseline incident-only strict history vs expanded prior pool | probe artifact + markdown + tests | compare is reproducible and honest |
| `TP2W3_CLOSEOUT_AND_SUCCESSOR_DECISION` | close family and route residuals | closeout docs + status/workset freeze | next step is explicit |

---

## 5. Verification Ladder

### Layer A — active-slice proof
- fail-first targeted tests
- implementation
- targeted tests green

### Layer B — script-backed proof
- run `python3 scripts/run_temporal_prior_probe.py`
- read back generated artifacts

### Layer C — regression proof
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Exit Criteria

family closeout requires:

1. exact-time temporal prior catalog landed
2. strict-cutoff prior probe landed
3. artifacts are refreshed and readable
4. closeout docs and successor routing written
5. full regression green
