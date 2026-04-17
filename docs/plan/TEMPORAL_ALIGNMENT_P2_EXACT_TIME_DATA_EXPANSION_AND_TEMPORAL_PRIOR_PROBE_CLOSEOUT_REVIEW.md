# TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_CLOSEOUT_REVIEW

- Family: `TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE`
- Closeout verdict: `accept_with_residuals`
- Date: 2026-04-17
- Branch: `main`

---

## 1. Scope Actually Completed

本 family 已真实落地并验证：

1. exact-time temporal prior catalog from packet-linked history
2. strict-cutoff compare between baseline incident-only history and expanded prior pool
3. script-backed artifacts for catalog / summary / probe
4. closeout + successor routing

## 2. Landed Surfaces

### Code
- `fixit_ai/temporal_alignment.py`

### Scripts
- `scripts/run_temporal_prior_probe.py`

### Tests
- `tests/test_temporal_alignment.py`

### Artifacts
- `data/eval/temporal-prior-catalog.jsonl`
- `data/eval/temporal-prior-summary.json`
- `data/eval/temporal-prior-probe.json`
- `data/eval/temporal-prior-probe.md`

## 3. Verified Truth

### Exact-time prior catalog
- packet-linked exact-time priors = `10`
- service mix:
  - `g-crm-campaign = 7`
  - `prod-hq-bff-service = 3`
- severity mix:
  - `severe = 4`
  - `moderate = 5`
  - `low = 1`
- action mix:
  - `page_owner = 4`
  - `create_ticket = 5`
  - `observe = 1`

### Strict-cutoff prior probe
- baseline strict history docs = `4`
- expanded packet prior count = `10`
- expanded total docs = `14`
- compare truth:
  - `folds_with_expanded_history_gt_baseline = 2`
  - `folds_with_expanded_refs_gt_baseline = 2`
  - `folds_with_top_hit_delta = 2`
  - `max_added_history_docs = 6`

Interpretation:

- P2 成功把 exact-time history surface 扩出来了
- expanded priors 确实改变了部分 fold 的 strict history coverage 与 retrieval top hits
- 但它尚未在当前小样本上带来 major packet / episode metrics lift

### Metrics remain flat
- baseline packet severe recall = `1.0`
- expanded packet severe recall = `1.0`
- baseline packet top-K precision = `1.0`
- expanded packet top-K precision = `1.0`
- baseline episode top-K precision = `0.3333`
- expanded episode top-K precision = `0.3333`

## 4. Validation Evidence

### Targeted
```bash
python3 -m unittest tests.test_temporal_alignment -v
```

### Script-backed
```bash
python3 scripts/run_temporal_prior_probe.py
```

### Regression
```bash
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal tests green (`11 tests`)
- prior-probe script green
- full regression green (`45 tests`)

## 5. Improvements Closed

1. repo now has a reusable exact-time temporal prior catalog instead of only 4 historical incident docs
2. strict-cutoff compare can now measure expanded prior coverage and top-hit deltas honestly
3. temporal P2 no longer depends on speculative narrative; it is artifact-backed

## 6. Residuals

1. earliest folds still have zero strict history because current cutoff discipline and event ordering leave no earlier exact-time priors
2. expanded priors improved coverage visibility but not major packet/episode metrics on current sample
3. next gain likely depends on boundary-safe cutoff review and/or higher-signal prior compaction, not simply adding more packet copies
4. blocked `DV2` mainline gate remains untouched

## 7. Honest Closeout

本 family 已完成其 admitted P2 范围，因此可以 closeout。

但 closeout 结论必须保持诚实：

- P2 已证明 exact-time prior expansion 在 coverage / retrieval visibility 上有价值
- P2 没有证明当前 sample 上的关键指标提升
- 下一步若继续 temporal 深化，应优先做 boundary-safe cutoff review 与更高信号的 prior ablation，而不是把当前结果包装成已证实的模型提升
