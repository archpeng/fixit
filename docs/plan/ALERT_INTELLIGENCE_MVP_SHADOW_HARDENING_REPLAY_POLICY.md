# ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_REPLAY_POLICY

- Family: `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING`
- Status: frozen-for-closeout
- Last verified: 2026-04-16

---

## 1. Purpose

当前 policy 的目标是把 replay inputs 从“一次性样本堆”收紧为**可重建、可解释、可审计**的 hardening contract。

## 2. Canonical Input Classes

### `live_bounded_export`

定义：

- 来自 observability / control-plane truth 的 bounded export
- 可以 out-of-band 刷新
- 允许在未来 refresh 中替换，但必须保留 manifest 记录

当前例子：

- `data/samples/raw/metrics_windows.jsonl`
- `data/samples/raw/log_evidence.jsonl`
- `data/samples/raw/trace_evidence.jsonl`
- `data/samples/raw/topology.jsonl`

### `retained_fixture`

定义：

- versioned local replay seed
- 用于 hardening、deterministic tests、larger replay coverage
- 不应伪装成 live truth

当前例子：

- `data/samples/fixtures/*.retained.jsonl`
- `data/eval/fixtures/*.retained.jsonl`
- `data/eval/historical_incidents.jsonl`
- `data/eval/training_examples.jsonl`
- `data/eval/outcomes.jsonl`
- `data/eval/manual_teacher_judgements.jsonl`

### `derived_artifact`

定义：

- 由 scripts/pipeline 生成
- 不允许 hand-edit
- 必须在 manifest 中只读登记

当前例子：

- `data/samples/candidate-windows.jsonl`
- `data/samples/incident-packets.jsonl`
- `data/eval/retrieval-index.json`
- `data/eval/label-ledger.json`
- `data/eval/calibration-report.json`
- `data/eval/teacher-request-ledger.jsonl`
- `data/eval/teacher-review-ledger.jsonl`
- `data/eval/teacher-fallback-ledger.jsonl`
- `data/eval/enrichment-usage.json`
- `data/eval/control-plane-live-readback.json`
- `data/reports/daily-shadow-report.{json,md}`

## 3. Refresh Rule

replay refresh 的 canonical command：

```bash
python3 scripts/refresh_replay_pack.py
```

其职责：

- 合并 live bounded exports + retained fixtures
- 生成 replay outputs：
  - `data/samples/replay/*.jsonl`
  - `data/eval/replay/*.jsonl`
- 写出：
  - `data/samples/replay-pack-manifest.json`

## 4. Determinism Rule

在相同输入文件集下：

- refresh 必须生成同一 replay pack 内容
- manifest 必须可重建 dataset row counts / file hash / source class
- 不能依赖隐藏 notebook 或未版本化临时文件

## 5. Policy Boundary

本 policy 不要求：

- live truth 永远可用
- control-plane service entry 一定存在
- teacher review 一定全部命中 real review

本 policy 要求：

- live truth 不可用时，必须显式 fallback
- retained fixtures 不可冒充 live truth
- derived artifacts 必须可重建

## 6. Current Readback

当前 hardening closeout 时，replay pack 已扩到：

- `9` datasets
- 同时包含 `live_bounded_export` 与 `retained_fixture`
- manifest 已记录 dataset row counts、source hashes、derived artifacts existence
