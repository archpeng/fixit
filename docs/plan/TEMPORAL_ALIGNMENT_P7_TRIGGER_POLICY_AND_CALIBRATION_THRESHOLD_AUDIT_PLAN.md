# TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT`
- Created: 2026-04-17
- Plan type: repo-global temporal P7 execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT`
- Governing reference:
  - `docs/architecture/fixit-temporal-decision-surface-admission-ladder.md`
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/architecture/fixit-temporal-decision-surface-admission-ladder.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_SUCCESSOR_ADMISSION.md`
  - `data/eval/temporal-selective-hybrid-probe.json`
  - `AGENTS.md`

---

## 1. Goal

把 temporal P6 的 retrieval-side evidence 推到 decision-surface audit：

1. build a bounded trigger-policy compare for raw vs temporal-aware routing
2. build a calibration-threshold audit that identifies the narrowest temporal policy band worth testing
3. keep the family inside the P7 ladder role rather than drifting into queue/action/runtime admission work
4. close the family honestly with either `continue_to_P8` or `collapse_temporal_ladder_here`

---

## 2. In Scope

- `fixit_ai/temporal_alignment.py` P7 extension
- trigger-policy compare under anti-leakage discipline
- calibration-threshold audit
- script-backed json/md artifacts
- closeout docs and successor routing

---

## 3. Out of Scope

- queue routing utility compare (`P8` only)
- shadow action policy integration (`P9` only)
- runtime admission / config / guardrails (`P10` only)
- bypassing blocked `DV2` schema gate
- claiming production metric lift
- introducing long-sequence temporal modeling

---

## 4. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TP7W1_TRIGGER_POLICY_COMPARE` | audit raw vs temporal-aware trigger policy | trigger-policy builder + tests | bounded non-empty policy delta is measurable and leak-safe |
| `TP7W2_CALIBRATION_THRESHOLD_AUDIT` | identify the narrowest temporal threshold band worth carrying forward | threshold audit builder + script-backed artifacts + tests | threshold recommendation is explicit and honest |
| `TP7W3_CLOSEOUT_AND_SUCCESSOR_DECISION` | close P7 and route next step | closeout docs + status/workset freeze | `continue_to_P8` or `collapse_here` is explicit |

---

## 5. Verification Ladder

### Layer A — active-slice proof
- fail-first targeted tests
- implementation
- targeted tests green

### Layer B — script-backed proof
- run `python3 scripts/run_temporal_trigger_policy_audit.py`
- read back generated artifacts

### Layer C — regression proof
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Exit Criteria

family closeout requires:

1. trigger-policy compare landed
2. calibration-threshold audit landed
3. artifacts are refreshed and readable
4. closeout docs and successor/collapse routing written
5. full regression green
6. final verdict explicitly states whether the ladder should continue to `P8` or stop at `P7`
