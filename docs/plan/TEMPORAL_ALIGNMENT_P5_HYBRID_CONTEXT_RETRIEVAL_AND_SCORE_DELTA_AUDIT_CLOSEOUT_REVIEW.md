# TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_CLOSEOUT_REVIEW

- Family: `TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT`
- Closeout verdict: `accept_with_residuals`
- Date: 2026-04-17
- Branch: `main`

---

## 1. Scope Actually Completed

本 family 已真实落地并验证：

1. bounded hybrid retrieval fusion between raw packet priors and episode-context priors
2. score-delta audit between raw-only and hybrid retrieval
3. script-backed artifacts for hybrid probe
4. closeout + successor routing

## 2. Landed Surfaces

### Code
- `fixit_ai/temporal_alignment.py`

### Scripts
- `scripts/run_temporal_hybrid_context_probe.py`

### Tests
- `tests/test_temporal_alignment.py`

### Artifacts
- `data/eval/temporal-hybrid-context-probe.json`
- `data/eval/temporal-hybrid-context-probe.md`

## 3. Verified Truth

### Hybrid score-delta compare
- hybrid context prior count = `4`
- `packets_with_hybrid_score_delta_gt_raw = 6`
- `packets_with_agreement_bonus = 6`
- `folds_with_top_hit_overlap = 3`
- `max_top_score_delta = 0.05`
- `anti_leakage_violation_count = 0`

Interpretation:

- hybrid fusion is now a real bounded retrieval lane rather than a design idea
- in 6 packets, hybrid agreement between raw/context lanes increased the top retrieval score
- anti-leakage discipline stayed clean

### Fold truth
- `ep_inc-compile-warmup`
  - score-delta packets = `2`
  - agreement-bonus packets = `2`
- `ep_inc-queue-depth`
  - raw priors = `3`
  - hybrid context priors = `2`
  - score-delta packets = `1`
- `ep_inc-other-service`
  - raw priors = `7`
  - hybrid context priors = `3`
  - score-delta packets = `3`
  - top-hit overlap = `true`

### Metrics remain flat
- raw packet severe recall = `1.0`
- hybrid packet severe recall = `1.0`
- raw packet top-K precision = `1.0`
- hybrid packet top-K precision = `1.0`
- raw episode top-K precision = `0.3333`
- hybrid episode top-K precision = `0.3333`

## 4. Validation Evidence

### Targeted
```bash
python3 -m unittest tests.test_temporal_alignment -v
```

### Script-backed
```bash
python3 scripts/run_temporal_hybrid_context_probe.py
```

### Regression
```bash
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal tests green (`16 tests`)
- hybrid-context probe script green
- full regression green (`50 tests`)

## 5. Improvements Closed

1. temporal lane now supports explicit raw/context hybrid retrieval fusion
2. score-delta audit is now artifact-backed instead of speculative
3. agreement-bonus behavior is measurable and bounded

## 6. Residuals

1. earliest fold still has zero history because no exact-time rows predate the first episode
2. hybrid score gains improved retrieval confidence shape but still did not move major packet / episode metrics on current sample
3. next likely value is selective hybrid routing or calibration-oriented audit, not simply always-on fusion
4. blocked `DV2` mainline gate remains untouched

## 7. Honest Closeout

本 family 已完成其 admitted P5 范围，因此可以 closeout。

但 closeout 结论必须保持诚实：

- P5 已证明 hybrid retrieval 和 score-delta audit 在离线分析面有价值
- P5 没有证明当前 sample 上的关键指标提升
- 若继续 temporal 深化，下一步应优先试 selective hybrid routing / calibration audit，而不是把当前结果包装成已证实的模型增益
