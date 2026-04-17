# TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION`
- Created: 2026-04-17
- Plan type: repo-global temporal P4 execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION`
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION_SUCCESSOR_ADMISSION.md`
  - `data/eval/temporal-boundary-safe-probe.json`
  - `AGENTS.md`

---

## 1. Goal

把 temporal P3 residual 压成真实代码、tests、artifacts：

1. synthesize richer episode-context priors from packet-linked reviewed history
2. compare episode-context priors against boundary-safe raw priors under continued anti-leakage discipline
3. quantify signal-ablation effects on doc-count reduction and retrieval overlap
4. close family honestly with successor routing

---

## 2. In Scope

- `fixit_ai/temporal_alignment.py` P4 extension
- episode-context prior synthesis
- signal-ablation compare artifact
- script-backed json/jsonl/md outputs
- closeout docs and successor routing

---

## 3. Out of Scope

- bypassing blocked `DV2` schema gate
- pretending P4 already proves production metric lift
- temporal sidecar production landing
- replacing packet as canonical decision unit
- fabricating exact timestamps from coarse text hints

---

## 4. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TP4W1_EPISODE_CONTEXT_PRIOR_SYNTHESIS` | synthesize one richer context prior per source episode | context prior builder + summary + tests | synthesized priors are bounded, leak-safe, and reproducible |
| `TP4W2_SIGNAL_ABLATION_COMPARE` | compare episode-context priors against boundary-safe raw priors | probe artifact + markdown + tests | compare is reproducible and honest |
| `TP4W3_CLOSEOUT_AND_SUCCESSOR_DECISION` | close family and route residuals | closeout docs + status/workset freeze | next step is explicit |

---

## 5. Verification Ladder

### Layer A — active-slice proof
- fail-first targeted tests
- implementation
- targeted tests green

### Layer B — script-backed proof
- run `python3 scripts/run_temporal_episode_context_probe.py`
- read back generated artifacts

### Layer C — regression proof
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Exit Criteria

family closeout requires:

1. episode-context prior synthesis landed
2. signal-ablation compare landed
3. artifacts are refreshed and readable
4. closeout docs and successor routing written
5. full regression green
