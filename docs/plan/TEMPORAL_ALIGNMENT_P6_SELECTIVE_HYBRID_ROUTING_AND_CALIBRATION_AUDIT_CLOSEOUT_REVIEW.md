# TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_CLOSEOUT_REVIEW

- Family: `TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT`
- Closeout verdict: `accept_with_residuals`
- Date: 2026-04-17
- Branch: `main`

---

## 1. Scope Actually Completed

本 family 已真实落地并验证：

1. selective hybrid routing instead of always-on hybrid fusion
2. calibration-oriented audit for where selective score delta matters
3. script-backed artifacts for selective hybrid probe
4. closeout + successor routing

## 2. Landed Surfaces

### Code
- `fixit_ai/temporal_alignment.py`

### Scripts
- `scripts/run_temporal_selective_hybrid_probe.py`

### Tests
- `tests/test_temporal_alignment.py`

### Artifacts
- `data/eval/temporal-selective-hybrid-probe.json`
- `data/eval/temporal-selective-hybrid-probe.md`

## 3. Verified Truth

### Selective hybrid compare
- `packets_selected_for_hybrid = 5`
- `packets_with_selected_score_delta_gt_raw = 5`
- `packets_with_selected_confidence_delta_gt_raw = 0`
- `folds_with_selective_routing = 3`
- `folds_with_top_hit_overlap = 3`
- `max_selected_top_score_delta = 0.05`
- `anti_leakage_violation_count = 0`

Interpretation:

- selective hybrid routing is now a real bounded lane rather than an always-on heuristic suggestion
- in 5 packets, selective routing kept the agreement-backed retrieval score lift
- but those score lifts did not translate into confidence lift under the current student surface

### Fold truth
- `ep_inc-compile-warmup`
  - selected hybrid packets = `2`
  - score-delta packets = `2`
- `ep_inc-queue-depth`
  - selected hybrid packets = `1`
  - score-delta packets = `1`
- `ep_inc-other-service`
  - selected hybrid packets = `2`
  - score-delta packets = `2`
  - top-hit overlap = `true`

### Metrics remain flat
- raw packet severe recall = `1.0`
- selective packet severe recall = `1.0`
- raw packet top-K precision = `1.0`
- selective packet top-K precision = `1.0`
- raw episode top-K precision = `0.3333`
- selective episode top-K precision = `0.3333`

## 4. Validation Evidence

### Targeted
```bash
python3 -m unittest tests.test_temporal_alignment -v
```

### Script-backed
```bash
python3 scripts/run_temporal_selective_hybrid_probe.py
```

### Regression
```bash
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal tests green (`17 tests`)
- selective-hybrid probe script green
- full regression green (`51 tests`)

## 5. Improvements Closed

1. temporal lane now has a bounded selective hybrid routing surface rather than only always-on hybrid fusion
2. score-delta usefulness is now audited at the selected-packet level
3. anti-leakage discipline remained intact while narrowing the hybrid lane

## 6. Residuals

1. earliest fold still has zero history because no exact-time rows predate the first episode
2. selective score gains improved retrieval score shape but did not increase student confidence or major packet / episode metrics on current sample
3. next likely value is trigger-policy / calibration-threshold audit, not more retrieval fusion alone
4. blocked `DV2` mainline gate remains untouched

## 7. Honest Closeout

本 family 已完成其 admitted P6 范围，因此可以 closeout。

但 closeout 结论必须保持诚实：

- P6 已证明 selective hybrid routing 和 calibration-style score audit 在离线分析面有价值
- P6 没有证明当前 sample 上的关键指标提升
- 若继续 temporal 深化，下一步应优先试 trigger-policy / calibration-threshold audit，而不是把当前结果包装成已证实的模型增益
