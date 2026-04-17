# TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT`
- Created: 2026-04-17
- Plan type: repo-global temporal P6 execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT`
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_SUCCESSOR_ADMISSION.md`
  - `data/eval/temporal-hybrid-context-probe.json`
  - `AGENTS.md`

---

## 1. Goal

把 temporal P5 residual 压成真实代码、tests、artifacts：

1. build a selective hybrid routing lane instead of always-on hybrid fusion
2. audit where score delta actually matters under bounded agreement-backed conditions
3. quantify calibration-oriented effects without faking metric lift
4. close family honestly with successor routing

---

## 2. In Scope

- `fixit_ai/temporal_alignment.py` P6 extension
- selective hybrid routing rules
- calibration-oriented score-delta audit
- script-backed json/md outputs
- closeout docs and successor routing

---

## 3. Out of Scope

- bypassing blocked `DV2` schema gate
- pretending P6 already proves production metric lift
- temporal sidecar production landing
- replacing packet as canonical decision unit
- fabricating exact timestamps from coarse text hints

---

## 4. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TP6W1_SELECTIVE_HYBRID_ROUTING` | route hybrid only on bounded agreement-backed cases | selective routing builder + tests | routing is bounded, reproducible, and leak-safe |
| `TP6W2_CALIBRATION_AUDIT` | audit where selective score delta matters | selective hybrid probe + markdown + tests | compare is reproducible and honest |
| `TP6W3_CLOSEOUT_AND_SUCCESSOR_DECISION` | close family and route residuals | closeout docs + status/workset freeze | next step is explicit |

---

## 5. Verification Ladder

### Layer A — active-slice proof
- fail-first targeted tests
- implementation
- targeted tests green

### Layer B — script-backed proof
- run `python3 scripts/run_temporal_selective_hybrid_probe.py`
- read back generated artifacts

### Layer C — regression proof
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Exit Criteria

family closeout requires:

1. selective hybrid routing landed
2. calibration-oriented score-delta audit landed
3. artifacts are refreshed and readable
4. closeout docs and successor routing written
5. full regression green
