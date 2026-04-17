# fixit 下一阶段推荐运行架构

- Status: `proposed-next-stage-ssot`
- Scope: `next-stage runtime / collection / scoring / review / label accumulation`
- Repo: `/home/peng/dt-git/github/fixit`
- Last updated: `2026-04-16`
- Primary reader: 后续继续实现 `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP` 的执行者

---

## 1. Decision Summary

### 1.1 Chosen approach

下一阶段默认采用：

- `incident packet` 继续作为 canonical decision unit
- 扩大自动收集的重点放在 `telemetry -> candidate window -> incident packet`
- 默认运行形态采用 **两段打分 + 人工 gate**
- **三段打分**（本地小模型 -> 高成本 teacher -> human）先不进入主运行面，只保留为后续 admission target
- 每日积累对象优先是：
  - `packet`
  - `teacher request / review / fallback`
  - `human-confirmed outcome / training label`
  - `calibration / phase progress artifacts`

### 1.2 Rejected for now

当前不采用：

- 全量原始日志直接送入大小模型阅读
- 本地小模型作为当前第一层主判官
- 全自动、无人工 gate 的标签闭环
- 在 schema / budget / rollback 未冻结前直接进入 local-small-model implementation

---

## 2. Current Truth That Governs This Decision

### 2.1 Already true in repo

当前仓库已具备：

- replay refresh: `scripts/refresh_replay_pack.py`
- packet build: `scripts/build_packets.py`
- retrieval/index: `scripts/build_retrieval_index.py`, `scripts/run_retrieval.py`
- cheap student scoring: `scripts/train_student.py`
- teacher workflow: `scripts/run_teacher_review.py`
- shadow eval/report: `scripts/evaluate_shadow.py`, `scripts/generate_shadow_report.py`
- data / teacher accumulation readout: `scripts/run_data_teacher_accumulation.py`
- full bounded hardening pipeline: `scripts/run_hardening_pipeline.py`

### 2.2 Current hard facts

- replay coverage now includes `2` services:
  - `g-crm-campaign`
  - `prod-hq-bff-service`
- current phase-2 refresh verdict: `not-yet`
- current reviewed teacher count used by accumulation readout: `2`
- target reviewed teacher count before rerunning small-model review: `10`
- current schema stability history elapsed days: `1`
- target schema stability window: `14 days`
- current local model deployment review: `not_ready`
- current teacher budget config:
  - `max_reviews_per_run = 2`
  - `max_tokens_per_run = 4000`
- current candidate generation script still bounds allowed services to:
  - `configs/services.yaml -> pilot_family.service`
  - current value: `g-crm-campaign`

### 2.3 Consequence

下一阶段的瓶颈不是“先缺一个更强语义模型”，而是：

- packet 生产面需要扩到小规模多 pilot 连续运行
- teacher reviewed volume 需要更快增长
- schema contract 需要先稳定一段时间
- 人工 outcome / label 回流需要日更化，而不是偶发补录

---

## 3. Canonical Data Flow

下一阶段的默认数据流如下。

```text
bounded raw telemetry
  -> replay refresh
  -> candidate windows
  -> incident packets
  -> retrieval + cheap scoring
  -> teacher review on hard cases
  -> human gate on risky / unresolved cases
  -> outcomes / training labels / incident summaries
  -> daily calibration + accumulation readout
```

### 3.1 Source -> target mapping

- `data/samples/raw/metrics_windows.jsonl` -> `data/samples/replay/metrics_windows.jsonl` -> `data/samples/candidate-windows.jsonl`
- `data/samples/raw/log_evidence.jsonl` -> `data/samples/replay/log_evidence.jsonl` -> `data/samples/incident-packets.jsonl`
- `data/samples/raw/trace_evidence.jsonl` -> `data/samples/replay/trace_evidence.jsonl` -> `data/samples/incident-packets.jsonl`
- `data/samples/raw/topology.jsonl` + control-plane live snapshot -> `data/samples/replay/topology.jsonl` -> packet topology fields
- `data/samples/raw/memory_summaries.jsonl` -> `data/samples/replay/memory_summaries.jsonl` -> packet history fields
- `data/eval/historical_incidents.jsonl` -> `data/eval/replay/historical_incidents.jsonl` -> `data/samples/retrieval-results.jsonl`
- `data/eval/training_examples.jsonl` -> `data/eval/replay/training_examples.jsonl` -> `data/eval/student-scores.jsonl`
- `data/eval/manual_teacher_judgements.jsonl` -> `data/eval/replay/manual_teacher_judgements.jsonl` -> `data/eval/teacher-judgements.jsonl`
- `data/eval/outcomes.jsonl` -> `data/eval/replay/outcomes.jsonl` -> `data/eval/metrics-summary.json`
- `data/eval/teacher-review-ledger.jsonl` + `data/eval/outcomes.jsonl` -> `data/eval/data-teacher-review-ledger.json`

### 3.2 Why the packet stays canonical

下一阶段即使扩大采集，也仍然不把“全量原始日志 body”作为直接判决单元；判决单元继续保持为 `incident packet`。

理由：

- 易回放
- 易评测
- 易做 retrieval
- 易做 teacher 请求裁剪
- 易接入 topology / owner / repo / history
- 易控制 token 与人工成本

---

## 4. Recommended Runtime: Two-Stage Scoring + Human Gate

### 4.1 Stage 0 — collection and packetization

#### Goal

自动扩大数据积累面，但只扩大到“bounded telemetry + packet”层，不扩大到“全量 raw log 直接模型阅读”层。

#### What runs

1. `scripts/refresh_replay_pack.py`
2. `scripts/generate_candidate_windows.py`
3. `scripts/check_control_plane_live_availability.py`
4. `scripts/build_packets.py`
5. `scripts/build_retrieval_index.py`
6. `scripts/run_retrieval.py`

#### Required outputs

- `data/samples/replay-pack-manifest.json`
- `data/samples/candidate-windows.jsonl`
- `data/samples/incident-packets.jsonl`
- `data/samples/retrieval-results.jsonl`
- `data/eval/retrieval-index.json`
- `data/eval/control-plane-live-readback.json`
- `data/eval/enrichment-usage.json`

#### Next-stage recommendation

- 保持 `bounded export`，但把 packet 生产从单 pilot 扩到小规模多 pilot allowlist
- 不建议直接把服务扩成“全服务无限制采样”
- 先扩成 `2-5` 个 pilot service family，再看 teacher / human 负载

### 4.2 Stage 1 — cheap dense scoring

#### Goal

对所有 `incident packet` 做低成本、高密度的第一轮判断。

#### Components

- rules / thresholds
- retrieval references
- current structured student scorer
- topology / owner / blast radius features

#### Current repo implementation

- `scripts/train_student.py`
- `data/eval/student-scores.jsonl`
- `data/eval/feature-manifest.json`
- `data/eval/student-threshold-proposal.json`

#### Expected outputs per packet

- `severity_score`
- `novelty_score`
- `confidence`
- `route_target`
- `needs_teacher`
- `reason_codes`

#### Admission state

- `can_run_now = yes`
- `recommended_now = yes`

#### Rule

下一阶段先把这一层跑密，而不是先换成小模型。

### 4.3 Stage 2 — high-cost teacher review

#### Goal

只让高成本模型处理高价值难例，而不是处理全部 packet。

#### Trigger rules

按当前配置，满足下列任一条件可进入 teacher：

- `confidence < 0.35`
- `novelty >= 0.85`
- `blast_radius >= 0.80`
- `severity_score >= 0.65`
- 或 decision mixer 额外判为规则冲突 / 高风险动作样本

#### Current repo implementation

- `scripts/run_teacher_review.py`
- outputs:
  - `data/eval/teacher-judgements.jsonl`
  - `data/eval/teacher-request-ledger.jsonl`
  - `data/eval/teacher-review-ledger.jsonl`
  - `data/eval/teacher-fallback-ledger.jsonl`
  - `data/eval/teacher-queue-summary.json`

#### Admission state

- `can_run_now = yes`
- `recommended_now = yes`
- `current_budget_is_enough_for_followup = no`

#### Required next-stage change

当前 `max_reviews_per_run = 2` 只适合 bounded MVP；若要加快下一阶段积累，应优先：

- 提高单次 teacher budget，或
- 增加每日 run 次数

目标不是扩大 teacher 覆盖面到全部 packet，而是更快补齐 `reviewed teacher count >= 10` 的 gate。

### 4.4 Human gate — action confirmation and gold labels

#### Goal

把 human 从“全量阅读者”变成“少量高价值最终判定者”。

#### Human should review

- 所有 `teacher fallback` 样本
- 所有拟执行 `page_owner` / `page_owner_and_escalate` 的样本
- 所有 teacher 与 cheap scorer 冲突的样本
- 所有高 blast radius 且 teacher confidence 仍低的样本
- 日终 incident / rollback / customer-impact 确认样本

#### Human outputs should land in

- `data/eval/outcomes.jsonl`
- `data/eval/training_examples.jsonl`
- `data/eval/historical_incidents.jsonl`

#### Recommended storage rule

- `outcomes.jsonl`: 存最终真实后验结果
- `training_examples.jsonl`: 存可用于 student 训练的确认样本
- `historical_incidents.jsonl`: 存已解决 incident 的检索摘要

#### Admission state

- `can_run_now = yes`
- `recommended_now = yes`

---

## 5. Two-Stage vs Three-Stage Loop

## 5.1 Recommended now: two-stage scoring

### Shape

```text
incident packet
  -> Stage 1 cheap scorer (rules + retrieval + current student)
  -> Stage 2 teacher LLM on selected hard cases
  -> human gate on risky / unresolved actions
  -> outcomes + labels backfill
```

### Why this is the default now

- repo 已有完整实现面
- 当前 bottleneck 是 review volume 与 schema stability，不是 semantic model 缺失
- 当前 local-small-model review verdict 仍是 `not-yet`
- 当前 local budget / latency / rollback 仍未冻结

### What this loop optimizes

- packet throughput
- teacher review quality
- label quality
- calibration correctness
- replay comparability

## 5.2 Deferred target: three-stage scoring

### Shape

```text
incident packet
  -> Stage 1 local small model dense first pass
  -> Stage 2 teacher LLM on uncertain / high-risk subset
  -> Stage 3 human final review on escalations / unresolved cases
  -> outcomes + labels backfill
```

### This stage is deferred behind gates

必须先满足：

- `reviewed teacher count >= 10`
- `schema stability >= 14 days`
- multi-pilot packet production已连续运行
- local model budget frozen
- latency budget frozen
- rollback plan frozen
- rerun review 能证明存在真实 semantic ROI，而不是单纯 review gap

### Current admission state

- `can_run_now = partially only in docs/review sense`
- `recommended_now = no`
- `implementation_admission = blocked`

---

## 6. Which Layers Can Start Now vs Must Wait

| Layer | Purpose | Current state | Next-stage decision |
|---|---|---|---|
| Stage 0 bounded telemetry harvest | 收集 metrics / logs / traces / topology / memory summaries | already present | start now |
| Replay refresh | 固化 replay / eval input base | already present | start now |
| Multi-pilot packet production | 扩大小规模服务覆盖 | partially present in replay, not yet in candidate allowlist | start now |
| Cheap dense scoring | rules + retrieval + current student | already present | start now |
| Teacher LLM hard-case review | 稀缺高成本裁决 | already present but budget-small | start now |
| Human gate | 最终高风险确认与 gold labels | process-needed | start now |
| Local small model dense first pass | 便宜语义预打分 | reviewed but not admitted | delay |
| Auto-promotion to implementation | 直接把 local model 放进主运行面 | not ready | delay |
| Full raw log corpus as training truth | 无限堆积原始日志正文 | architecturally discouraged | delay / avoid |
| All-service unbounded rollout | 无界服务覆盖 | not justified | delay |

---

## 7. Daily Packet / Teacher / Human Label Accumulation Runbook

## 7.1 Daily run objective

每天必须至少沉淀四类资产：

1. new / refreshed `incident packet`
2. new `teacher request / review / fallback` records
3. new `human-confirmed outcome / training labels`
4. refreshed `calibration / accumulation / shadow report`

## 7.2 Daily execution order

### A. Start of day — refresh bounded replay and packets

```bash
python3 scripts/refresh_replay_pack.py --generated-at <ISO8601>
python3 scripts/generate_candidate_windows.py --input data/samples/replay/metrics_windows.jsonl
python3 scripts/check_control_plane_live_availability.py
python3 scripts/build_packets.py \
  --candidates data/samples/candidate-windows.jsonl \
  --logs data/samples/replay/log_evidence.jsonl \
  --traces data/samples/replay/trace_evidence.jsonl \
  --topology data/samples/replay/topology.jsonl \
  --memory data/samples/replay/memory_summaries.jsonl \
  --services-config configs/services.yaml \
  --live-enrichment data/live/control_plane_service_context.jsonl \
  --enrichment-usage data/eval/enrichment-usage.json
python3 scripts/build_retrieval_index.py
python3 scripts/run_retrieval.py \
  --history data/eval/replay/historical_incidents.jsonl \
  --index data/eval/retrieval-index.json
```

#### Day-start outputs

- refreshed replay pack
- refreshed candidate windows
- refreshed packets
- refreshed retrieval index / results

### B. Mid-cycle — run cheap dense scoring

```bash
python3 scripts/train_student.py --training data/eval/replay/training_examples.jsonl
```

#### Mid-cycle outputs

- `data/eval/model.pkl`
- `data/eval/student-scores.jsonl`
- `data/eval/feature-manifest.json`
- `data/eval/student-threshold-proposal.json`

### C. Teacher batch — spend expensive review budget only on selected cases

```bash
python3 scripts/run_teacher_review.py \
  --seed-judgements data/eval/replay/manual_teacher_judgements.jsonl
```

#### Teacher outputs

- `data/eval/teacher-judgements.jsonl`
- `data/eval/teacher-request-ledger.jsonl`
- `data/eval/teacher-review-ledger.jsonl`
- `data/eval/teacher-fallback-ledger.jsonl`
- `data/eval/teacher-queue-summary.json`

#### Daily operating rule

- 不要求 teacher 看全部 packet
- 必须优先消化：
  - high novelty
  - high blast radius
  - low confidence
  - fallback candidates
  - rule/student conflict

### D. Human gate — same day or end of day

人工对以下样本做最终确认：

- `teacher fallback`
- `page_owner*` 类 action
- teacher 置信仍低的高风险样本
- 已产生真实 incident / rollback / customer impact 的样本

#### Human writes back to

- `data/eval/outcomes.jsonl`
- `data/eval/training_examples.jsonl`
- `data/eval/historical_incidents.jsonl`

#### Daily storage rule

- 每个 human-confirmed case 至少补一个 `outcome`
- 若该 case 对 student 有训练价值，再补一个 `training_examples` row
- 若该 case 能支持未来 retrieval，再补一个 `historical_incidents` summary

### E. End of day — refresh metrics, calibration, and accumulation truth

```bash
python3 scripts/evaluate_shadow.py \
  --outcomes data/eval/replay/outcomes.jsonl \
  --teacher-fallbacks data/eval/teacher-fallback-ledger.jsonl
python3 scripts/build_label_ledger.py
python3 scripts/build_calibration_report.py
python3 scripts/run_data_teacher_accumulation.py
python3 scripts/generate_shadow_report.py \
  --outcomes data/eval/replay/outcomes.jsonl \
  --manifest data/samples/replay-pack-manifest.json \
  --enrichment-usage data/eval/enrichment-usage.json \
  --teacher-summary data/eval/teacher-queue-summary.json
```

#### End-of-day outputs

- `data/eval/triage-decisions.jsonl`
- `data/eval/metrics-summary.json`
- `data/eval/label-ledger.json`
- `data/eval/calibration-report.json`
- `data/eval/data-teacher-*.json`
- `data/reports/daily-shadow-report.{json,md}`

---

## 8. Packet / Teacher / Human Label Storage Contract

## 8.1 Packet storage

### Must exist daily

- `data/samples/candidate-windows.jsonl`
- `data/samples/incident-packets.jsonl`
- `data/samples/retrieval-results.jsonl`

### Contract

- one row per candidate window / packet / retrieval result
- packet schema remains `schemas/incident-packet.v1.json`
- do not use raw log body archive as the primary training object

## 8.2 Teacher storage

### Must exist daily

- `data/eval/teacher-request-ledger.jsonl`
- `data/eval/teacher-review-ledger.jsonl`
- `data/eval/teacher-fallback-ledger.jsonl`
- `data/eval/teacher-judgements.jsonl`
- `data/eval/teacher-queue-summary.json`

### Contract

- request ledger = what was sent to teacher and why
- review ledger = what teacher actually reviewed
- fallback ledger = what teacher did not confidently resolve
- judgements = structured teacher output used by decision layer

## 8.3 Human label storage

### Must exist daily once human touched a case

- `data/eval/outcomes.jsonl`
- `data/eval/training_examples.jsonl`
- `data/eval/historical_incidents.jsonl`

### Contract

- `outcomes.jsonl` holds post-incident truth and operational consequence
- `training_examples.jsonl` holds supervised examples with label source provenance
- `historical_incidents.jsonl` holds compressed resolved-incident summaries for retrieval

---

## 9. Concrete Next-Stage Changes Recommended

## 9.1 Change now

1. widen candidate generation from single pilot service to a small explicit pilot allowlist
2. run the hardening pipeline or equivalent daily, not ad hoc
3. increase effective teacher throughput until reviewed teacher count clears `10`
4. require same-day human write-back for fallback / escalation cases
5. treat `run_data_teacher_accumulation.py` as a daily truth refresh, not a one-off report generator

## 9.2 Delay until gates pass

1. local small model dense first-pass implementation
2. local model latency budget enforcement in runtime
3. local model rollback orchestration
4. unbounded all-service rollout
5. direct full raw log corpus modeling

---

## 10. Minimum Admission Gates for the Next Promotion

下一阶段若要从“两段打分 + human gate”升级到“三段打分”，至少需要：

- `data/eval/data-teacher-phase2-refresh.json` 不再是 `not-yet`
- `teacher_reviewed_count >= 10`
- `schema_stability_days >= 14`
- local model budget frozen
- latency budget frozen
- rollback plan frozen
- widened pilot allowlist已经连续运行且未显著抬高 fallback burden

---

## 11. Recommended One-Command Wrapper for Daily Runtime

当前 repo 已有最接近的 wrapper：

```bash
python3 scripts/run_hardening_pipeline.py
```

下一阶段推荐做法：

- 保留该 wrapper 作为 daily bounded runtime baseline
- 后续只在 wrapper 内扩 allowlist、teacher budget、human write-back hooks
- 不先重写成“全新 local-small-model runtime”

---

## 12. Final Recommendation

当前最合理的下一阶段运行架构不是：

- `raw logs -> local small model -> big model -> human`

而是：

- `bounded telemetry -> incident packet -> cheap dense scorer -> teacher LLM on selected hard cases -> human gate -> outcomes/labels -> daily accumulation refresh`

等 `teacher volume / schema stability / budget / rollback` 四类 gate 都补齐后，再把：

- `local small model dense first pass`

加入为真正的第三段。
