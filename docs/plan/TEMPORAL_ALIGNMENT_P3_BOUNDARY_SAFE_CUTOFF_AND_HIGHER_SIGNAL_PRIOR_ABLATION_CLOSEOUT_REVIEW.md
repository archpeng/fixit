# TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION_CLOSEOUT_REVIEW

- Family: `TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION`
- Closeout verdict: `accept_with_residuals`
- Date: 2026-04-17
- Branch: `main`

---

## 1. Scope Actually Completed

本 family 已真实落地并验证：

1. boundary-safe cutoff review with explicit anti-leakage proof
2. compare between current strict `<` admissibility and boundary-safe admissibility
3. higher-signal compacted prior ablation against raw packet-copy priors
4. closeout + successor routing

## 2. Landed Surfaces

### Code
- `fixit_ai/temporal_alignment.py`
- `fixit_ai/retrieval_index.py`

### Scripts
- `scripts/run_temporal_boundary_safe_probe.py`

### Tests
- `tests/test_temporal_alignment.py`

### Artifacts
- `data/eval/temporal-boundary-safe-probe.json`
- `data/eval/temporal-boundary-safe-probe.md`

## 3. Verified Truth

### Boundary-safe cutoff compare
- fold count = `4`
- `folds_with_boundary_safe_history_gt_strict = 3`
- `folds_with_equality_admitted_docs = 3`
- `equality_admitted_doc_count = 4`
- `anti_leakage_violation_count = 0`

Interpretation:

- current strict `<` semantics were leaving valid exact-time rows on the table
- boundary-safe admissibility (`<=` at the end boundary) recovers additional history in 3 folds
- explicit anti-leakage audit stayed clean

### Higher-signal compacted prior ablation
- `folds_with_compacted_doc_count_lt_boundary_safe = 2`
- `folds_with_top_hit_overlap = 3`
- `max_docs_removed_by_compaction = 4`

Interpretation:

- fold-local compaction can reduce raw prior doc count materially
- in most folds with usable history, prototype/compacted priors still preserve top-hit overlap with raw priors

### Fold truth
- `ep_inc-compile-warmup`
  - strict history = `0`
  - boundary-safe history = `1`
- `ep_inc-queue-depth`
  - strict history = `2`
  - boundary-safe history = `3`
  - compacted priors = `2` vs raw priors `3`
- `ep_inc-other-service`
  - strict history = `8`
  - boundary-safe history = `10`
  - compacted priors = `3` vs raw priors `7`

### Metrics remain flat
- strict packet severe recall = `1.0`
- boundary-safe packet severe recall = `1.0`
- prototype packet severe recall = `1.0`
- strict packet top-K precision = `1.0`
- boundary-safe packet top-K precision = `1.0`
- prototype packet top-K precision = `1.0`
- strict episode top-K precision = `0.3333`
- boundary-safe episode top-K precision = `0.3333`
- prototype episode top-K precision = `0.3333`

## 4. Validation Evidence

### Targeted
```bash
python3 -m unittest tests.test_temporal_alignment -v
```

### Script-backed
```bash
python3 scripts/run_temporal_boundary_safe_probe.py
```

### Regression
```bash
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal tests green (`13 tests`)
- boundary-safe probe script green
- full regression green (`47 tests`)

## 5. Improvements Closed

1. cutoff boundary semantics are no longer only an assumption; they are artifact-backed and leak-audited
2. exact-time retrieval history now has a safer and richer admissibility compare surface
3. prototype / compacted priors are now measurable against raw packet-copy priors instead of being speculative

## 6. Residuals

1. earliest fold still has zero history because no exact-time rows exist before the first episode
2. boundary-safe + compaction improved retrieval surface shape but still did not move major packet / episode metrics on current sample
3. next value likely needs richer episode-context prior synthesis or stronger signal compression, not just more boundary tweaks
4. blocked `DV2` mainline gate remains untouched

## 7. Honest Closeout

本 family 已完成其 admitted P3 范围，因此可以 closeout。

但 closeout 结论必须保持诚实：

- P3 已证明 boundary-safe cutoff review 和 higher-signal prior compaction 都有离线价值
- P3 没有证明当前 sample 上的关键指标提升
- 若继续 temporal 深化，下一步应优先试 episode-context prior synthesis / stronger signal ablation，而不是把当前结果包装成已证实的模型增益
