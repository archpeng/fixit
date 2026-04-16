# ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_CLOSEOUT_REVIEW

- Family: `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION`
- Review verdict: `accept_with_residuals`
- Closeout date: 2026-04-16
- Execution mode: `execute -> review -> replan` loop with TDD for code-bearing waves

---

## 1. Final Verdict

当前 family 已达到 MVP foundation closeout 条件。

已完成：

- schema trio 冻结
- repo scaffold 与 config stubs 落地
- bounded pilot admission 完成
- candidate window -> packet builder 主链落地
- retrieval baseline 落地
- first student baseline 落地
- sparse teacher lane 落地
- shadow report / eval artifacts 落地
- `PLAN/STATUS/WORKSET` 已可 honest closeout

保留 residual，但不阻断当前 family closeout。

---

## 2. TDD / Verification Evidence

### Test command

```bash
python3 -m unittest discover -s tests -v
```

### Latest result

- `6 tests`
- `OK`

### Pipeline command

```bash
python3 scripts/run_shadow_pipeline.py
```

### Latest result

- candidate windows generated
- packets built
- retrieval results generated
- student model trained and scored
- teacher reviews selected and merged with seed judgement
- triage decisions evaluated
- shadow report rendered

---

## 3. Wave-by-Wave Review

### `WS0_FOUNDATION_FREEZE`

Landed:

- `schemas/incident-packet.v1.json`
- `schemas/teacher-judgement.v1.json`
- `schemas/triage-decision.v1.json`
- `configs/services.yaml`
- `configs/thresholds.yaml`
- `configs/teacher-budget.yaml`
- repo scaffold for `scripts/`, `data/samples/`, `data/eval/`, `data/reports/`

Review:

- schema 字段与 MVP 文档对齐
- triage / teacher / packet contract 可互相拼接

Replan outcome:

- admitted next wave `WS0.S2`，补 pilot boundary

### `WS0.S2_PILOT_ADMISSION_AND_REPLAY_BOUNDARY`

Landed:

- `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PILOT_ADMISSION.md`
- bounded pilot family: `g-crm-campaign / ADCService/Compile / 24h`

Review:

- pilot singular / bounded
- 有真实 runtime evidence 支撑

Replan outcome:

- admitted `WS1_PACKET_PATH`

### `WS1_PACKET_PATH`

Landed:

- `scripts/generate_candidate_windows.py`
- `scripts/build_packets.py`
- `data/samples/candidate-windows.jsonl`
- `data/samples/incident-packets.jsonl`
- raw sample exports under `data/samples/raw/`

Review:

- candidate generation 能同时覆盖 rule-hit 与 rule-missed 窗口
- packet builder 可拼接 logs / traces / topology / memory 并通过 schema 校验

Replan outcome:

- admitted `WS2_RETRIEVAL_BASELINE`

### `WS2_RETRIEVAL_BASELINE`

Landed:

- `fixit_ai/retrieval.py`
- `scripts/run_retrieval.py`
- `data/samples/retrieval-results.jsonl`
- `data/eval/historical_incidents.jsonl`

Review:

- severe compile incident `inc-compile-500` 能在 matching packet 上排名第一
- retrieval 输出可解释 `incident_id + similarity_score + severity + action`

Replan outcome:

- admitted `WS3_STUDENT_BASELINE`

### `WS3_STUDENT_BASELINE`

Landed:

- `fixit_ai/student.py`
- `scripts/train_student.py`
- `data/eval/model.pkl`
- `data/eval/student-scores.jsonl`
- `data/eval/feature-manifest.json`
- `data/eval/label-sources.json`
- `data/eval/feature-importance.md`
- `data/eval/student-threshold-proposal.json`

Review:

- severe packets score 高于 non-severe packets
- rule-missed hard case `ipk_w004` 仍能被高分命中

Replan outcome:

- admitted `WS4_TEACHER_LANE`

### `WS4_TEACHER_LANE`

Landed:

- `fixit_ai/teacher.py`
- `scripts/run_teacher_review.py`
- `data/eval/teacher-review-requests.jsonl`
- `data/eval/teacher-judgements.jsonl`

Review:

- hard-case selection obeys budget gate
- `ipk_w004` 被选为 novelty/high-score/rule-missed hard case

Replan outcome:

- admitted `WS5_SHADOW_EVAL_CLOSEOUT`

### `WS5_SHADOW_EVAL_CLOSEOUT`

Landed:

- `fixit_ai/shadow.py`
- `fixit_ai/eval.py`
- `scripts/evaluate_shadow.py`
- `scripts/generate_shadow_report.py`
- `scripts/run_shadow_pipeline.py`
- `data/eval/triage-decisions.jsonl`
- `data/eval/metrics-summary.json`
- `data/reports/daily-shadow-report.json`
- `data/reports/daily-shadow-report.md`

Review:

- `severe_recall = 1.0`
- `top_k_precision = 0.6667`
- `teacher_escalation_rate = 0.25`
- `missed_severe_count = 0`
- shadow report 包含 `rule-missed but model ranked high`

Replan outcome:

- current family 可 closeout
- successor admission 进入 hardening，而非本地小模型升级

---

## 4. Closeout Evidence Index

### Code / contract

- `fixit_ai/*.py`
- `scripts/*.py`
- `schemas/*.json`
- `configs/*.yaml`

### Sample / eval artifacts

- `data/samples/candidate-windows.jsonl`
- `data/samples/incident-packets.jsonl`
- `data/samples/retrieval-results.jsonl`
- `data/eval/student-scores.jsonl`
- `data/eval/teacher-judgements.jsonl`
- `data/eval/triage-decisions.jsonl`
- `data/eval/metrics-summary.json`
- `data/reports/daily-shadow-report.md`

### Control-plane / runtime admission evidence

- `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PILOT_ADMISSION.md`

---

## 5. Residuals

当前不阻断 closeout，但必须保留为下一 family 输入：

1. `jsonl` retrieval store 未来可升级为 richer vector index
2. student calibration 仍基于小样本，应在更大 replay window 上复核
3. teacher lane 当前使用 bounded seed judgement；后续需接真实 teacher workflow
4. topology / owner / repo 当前通过 bounded exports / config 进入 pipeline；后续需硬化 live control-plane ingestion
5. local small model student upgrade 尚未 admission

---

## 6. Successor Recommendation

推荐 successor family：

- `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING`

而不是立即进入：

- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE`

原因：

- 当前 foundation 已跑通，但 replay coverage、calibration、teacher workflow、live ingestion 仍需 hardening
- 先扩真实数据与 hardening，收益高于过早上本地小模型
