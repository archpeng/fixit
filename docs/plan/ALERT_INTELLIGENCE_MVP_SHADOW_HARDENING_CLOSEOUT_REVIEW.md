# ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_CLOSEOUT_REVIEW

- Family: `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING`
- Review verdict: `accept_with_residuals`
- Closeout date: 2026-04-16
- Execution mode: `execute -> review -> replan` loop with TDD for code-bearing waves

---

## 1. Final Verdict

当前 family 已达到 hardening closeout 条件。

已完成：

- replay pack manifest / refresh tooling / replay policy 冻结
- retrieval index 与 compat readout 落地
- larger replay coverage、label ledger、calibration report 落地
- teacher request/review/fallback ledgers 落地
- control-plane live availability readback + config fallback telemetry 落地
- hardened shadow report 已增加：
  - data freshness
  - fallback usage
  - teacher queue visibility
- `PLAN/STATUS/WORKSET` 可 honest closeout

仍保留 residual，但不阻断当前 family closeout。

---

## 2. TDD / Verification Evidence

### Test command

```bash
python3 -m unittest discover -s tests -v
```

### Latest result

- `12 tests`
- `OK`

### Hardening pipeline command

```bash
python3 scripts/run_hardening_pipeline.py
```

### Latest result

- replay pack refreshed
- control-plane live availability checked
- candidate windows regenerated from replay pack
- packets rebuilt with live-first enrichment and config fallback
- retrieval index + compat readout generated
- student rescored on expanded replay pack
- label ledger and calibration report generated
- teacher request/review/fallback ledgers generated
- triage decisions and metrics regenerated
- hardened shadow report rendered

---

## 3. Wave-by-Wave Review

### `HW0_REPLAY_BOUNDARY_FREEZE`

Landed:

- `configs/replay-pack.yaml`
- `fixit_ai/replay_pack.py`
- `scripts/refresh_replay_pack.py`
- `tests/test_hardening_pipeline.py`
- `data/samples/replay-pack-manifest.json`
- `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_REPLAY_POLICY.md`

Review:

- replay inputs 已区分为 `live_bounded_export` / `retained_fixture` / `derived_artifact`
- refresh 在固定输入下 deterministic

Replan outcome:

- admitted `HW1_RETRIEVAL_HARDENING`

### `HW1_RETRIEVAL_HARDENING`

Landed:

- `fixit_ai/retrieval_index.py`
- `scripts/build_retrieval_index.py`
- `data/eval/retrieval-index.json`
- `data/eval/retrieval-compat-readout.json`

Review:

- hardened retrieval 保留 explainable refs
- compat readout 显示 top hit 与 predecessor baseline 一致

Replan outcome:

- admitted `HW2_CALIBRATION_AND_LABEL_HARDENING`

### `HW2_CALIBRATION_AND_LABEL_HARDENING`

Landed:

- retained replay fixtures under:
  - `data/samples/fixtures/`
  - `data/eval/fixtures/`
- `fixit_ai/labeling.py`
- `fixit_ai/calibration.py`
- `scripts/build_label_ledger.py`
- `scripts/build_calibration_report.py`
- `data/eval/label-ledger.json`
- `data/eval/calibration-report.json`
- `data/eval/calibration-report.md`

Review:

- replay coverage 从 foundation 扩展到 `9` metric windows / `7` incidents / `10` training examples / `8` outcomes
- current threshold stance 可以被 artifact 解释：`recommended_action = keep`

Replan outcome:

- admitted `HW3_TEACHER_WORKFLOW_HARDENING`

### `HW3_TEACHER_WORKFLOW_HARDENING`

Landed:

- `fixit_ai/teacher.py` hardening extensions
- `scripts/run_teacher_review.py` hardening outputs
- `data/eval/teacher-request-ledger.jsonl`
- `data/eval/teacher-review-ledger.jsonl`
- `data/eval/teacher-fallback-ledger.jsonl`
- `data/eval/teacher-queue-summary.json`

Review:

- teacher queue 可审计
- bounded pilot 内出现：
  - `1` reviewed hard case
  - `1` fallback hard case
- fallback semantics 不再隐含在代码里

Replan outcome:

- admitted `HW4_LIVE_ENRICHMENT_HARDENING`

### `HW4_LIVE_ENRICHMENT_HARDENING`

Landed:

- `fixit_ai/enrichment.py`
- `scripts/check_control_plane_live_availability.py`
- `data/eval/control-plane-live-readback.json`
- `data/eval/enrichment-usage.json`
- `scripts/build_packets.py` live-first enrichment path

Review:

- control-plane health endpoint reachable
- pilot service `g-crm-campaign` 当前未命中 live service snapshot
- pipeline 因此显式使用 `config_fallback`
- live-first path 与 fallback path 都已可审计

Replan outcome:

- admitted `HW5_CLOSEOUT_AND_SUCCESSOR_ADMISSION`

### `HW5_CLOSEOUT_AND_SUCCESSOR_ADMISSION`

Landed:

- `scripts/run_hardening_pipeline.py`
- hardened `data/reports/daily-shadow-report.{json,md}`
- regenerated `data/eval/metrics-summary.json`

Review:

- `severe_recall = 1.0`
- `top_k_precision = 1.0`
- `teacher_escalation_rate = 0.1429`
- `missed_severe_count = 0`
- report 增加了：
  - `Data Freshness`
  - `Fallback Usage`
  - `Teacher Queue`

Replan outcome:

- current family 可 closeout
- successor admission 推荐转向 small-model readiness review，而不是直接实现本地小模型

---

## 4. Key Hardening Evidence

### Replay / policy

- `configs/replay-pack.yaml`
- `data/samples/replay-pack-manifest.json`
- `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_REPLAY_POLICY.md`

### Retrieval

- `data/eval/retrieval-index.json`
- `data/eval/retrieval-compat-readout.json`

### Calibration / label

- `data/eval/label-ledger.json`
- `data/eval/calibration-report.json`
- `data/eval/calibration-report.md`

### Teacher workflow

- `data/eval/teacher-request-ledger.jsonl`
- `data/eval/teacher-review-ledger.jsonl`
- `data/eval/teacher-fallback-ledger.jsonl`
- `data/eval/teacher-queue-summary.json`

### Enrichment

- `data/eval/control-plane-live-readback.json`
- `data/eval/enrichment-usage.json`

### Shadow / eval

- `data/eval/metrics-summary.json`
- `data/reports/daily-shadow-report.md`

---

## 5. Residuals

当前不阻断 closeout，但应进入 successor review：

1. 当前仍是单 pilot service family；尚未扩到 multi-service replay admission
2. control-plane live-first path 已实现，但当前真实 service snapshot 仍未命中，需要未来补真实 service-level live export
3. teacher lane 仍是 bounded review workflow，不等于 fully integrated external teacher system
4. local small model student 仍未实现，只具备更可靠的 review admission 基础

---

## 6. Successor Recommendation

推荐 successor family：

- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`

原因：

- replay / label / calibration / teacher / enrichment 已比 foundation 明显更硬化
- 已具备评审“是否值得进入本地小模型 student 实施”的前置证据
- 仍不建议直接跳到 small-model implementation family，先做 readiness review 更稳
