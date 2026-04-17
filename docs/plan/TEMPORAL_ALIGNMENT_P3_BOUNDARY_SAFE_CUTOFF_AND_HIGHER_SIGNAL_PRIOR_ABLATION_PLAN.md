# TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION`
- Created: 2026-04-17
- Plan type: repo-global temporal P3 execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE`
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_SUCCESSOR_ADMISSION.md`
  - `data/eval/temporal-prior-probe.json`
  - `AGENTS.md`

---

## 1. Goal

把 temporal P2 residual 压成真实代码、tests、artifacts：

1. review strict cutoff boundary semantics with explicit anti-leakage proof
2. compare boundary-safe admissibility against current strict `<` admissibility
3. compare higher-signal compacted priors against raw packet-copy priors under the reviewed cutoff discipline
4. close family honestly with successor routing

---

## 2. In Scope

- `fixit_ai/temporal_alignment.py` P3 extension
- boundary-safe cutoff compare
- higher-signal prior compaction / prototype ablation
- script-backed compare artifacts
- closeout docs and successor routing

---

## 3. Out of Scope

- bypassing blocked `DV2` schema gate
- pretending P3 already proves production metric lift
- temporal sidecar production landing
- replacing packet as canonical unit
- fabricating exact timestamps from coarse text hints

---

## 4. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TP3W1_BOUNDARY_SAFE_CUTOFF_REVIEW` | compare `<` vs boundary-safe admissibility with anti-leakage proof | boundary-safe compare builder + tests + artifact | equality-admitted rows are explicit and leakage stays zero |
| `TP3W2_HIGHER_SIGNAL_PRIOR_ABLATION` | compare compacted higher-signal priors vs raw packet-copy priors | compaction compare + tests + artifact | compare is reproducible and honest |
| `TP3W3_CLOSEOUT_AND_SUCCESSOR_DECISION` | close family and route residuals | closeout docs + status/workset freeze | next step is explicit |

---

## 5. Verification Ladder

### Layer A — active-slice proof
- fail-first targeted tests
- implementation
- targeted tests green

### Layer B — script-backed proof
- run `python3 scripts/run_temporal_boundary_safe_probe.py`
- read back generated artifacts

### Layer C — regression proof
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Exit Criteria

family closeout requires:

1. boundary-safe cutoff review landed
2. higher-signal prior ablation landed
3. artifacts are refreshed and readable
4. closeout docs and successor routing written
5. full regression green
