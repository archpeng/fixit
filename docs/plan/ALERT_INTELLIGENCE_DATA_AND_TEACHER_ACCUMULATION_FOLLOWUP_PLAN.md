# ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_PLAN

- Status: completed
- Family: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`
- Created: 2026-04-16
- Plan type: repo-global successor execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
- Source anchors:
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/mvp/alert-intelligence-mvp.md`
  - `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_SUCCESSOR_ADMISSION.md`
  - `data/eval/data-teacher-phase2-refresh.json`
  - `AGENTS.md`

---

## 1. Goal

把 `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md` 中冻结的下一阶段运行面，压成一个可连续执行的 bounded family：

- `bounded telemetry -> candidate window -> incident packet`
- `cheap dense scorer -> teacher hard-case review -> human gate`
- `outcomes / labels / historical incidents -> daily accumulation refresh`

本 family 的目标不是重开 small-model implementation，而是把以下缺口压成真实运行面与可追踪证据：

- multi-pilot runtime 不再受单服务 candidate allowlist 限制
- teacher reviewed volume 明显继续增长
- human write-back 进入 daily contract，而不是偶发补录
- schema stability history 变成 append-only daily checkpoint
- phase-2 refresh 在新证据下重新评估是否值得重开 review

边界是：

> 先把两段打分 + human gate 跑密、跑稳、跑出连续证据；在 review gate 未满足前，不引入 local small model dense first pass。

---

## 2. Scope

## 2.1 In scope

- small explicit pilot allowlist runtime activation
- candidate generation 从单 pilot service 扩到 bounded multi-pilot allowlist
- daily bounded runtime baseline readout
- teacher throughput / budget / batch selection 改进
- same-day human write-back contract for fallback / escalation cases
- label / outcome / historical incident backfill with provenance
- append-only schema stability checkpoints
- refreshed accumulation / calibration / shadow / phase-2 readouts
- family closeout + successor decision

## 2.2 Out of scope

- local small model training / serving / rollout
- direct full raw log corpus modeling
- all-service unbounded observability export
- production auto-action / unattended escalation
- synthetic / unprovenanced labels pretending to be teacher or human truth
- 绕过 `incident packet` 直接把 raw logs 当成 canonical decision unit

---

## 3. Entry Criteria

以下前置已满足：

- predecessor `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION` 已 closeout
- predecessor verdict = `accept_with_residuals`
- predecessor successor admission = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`
- next-stage runtime architecture doc 已冻结当前推荐运行形态
- 当前 hard facts:
  - `multi_pilot_replay_coverage = met`
  - `teacher_reviewed_volume_growth = partial`
  - `schema_stability_window = unmet`
  - `phase2_verdict = not-yet`
  - `current_teacher_reviewed_count = 2`
  - `target_teacher_reviewed_count = 10`
  - `teacher_label_gap = 1`
  - `current_schema_stability_days = 1`
  - `target_schema_stability_days = 14`
  - `teacher max_reviews_per_run = 2`
  - `teacher max_tokens_per_run = 4000`
- 当前 repo 已有可复用 surface：
  - `scripts/run_hardening_pipeline.py`
  - `scripts/run_data_teacher_accumulation.py`
  - `scripts/run_teacher_review.py`
  - `data/eval/*ledger*`
  - `data/eval/*phase2*`

当前最重要的未落地 truth：

- candidate generation 仍主要绑定 `configs/services.yaml -> pilot_family.service`
- daily runtime 还未冻结成“small explicit allowlist + teacher/human write-back”的 followup control surface

---

## 4. Family Exit Criteria

当以下条件同时满足时，本 family 可 closeout：

1. candidate generation / runtime wrapper 已支持 small explicit pilot allowlist，而不是单服务 hardcode
2. daily runtime baseline readout 已存在，并可证明 packet production 与 scoring path 不再只围绕一个 pilot service
3. teacher throughput / ledger evidence 已显式增长，且 reviewed teacher count 朝 `10` 前进并有 provenance
4. fallback / escalation cases 的 human write-back contract 已冻结，且 outcome / training / historical incident stores 有对应回写证据
5. schema stability history 已变成 append-only checkpoint；时间窗进度可真实读出
6. accumulation / calibration / shadow / phase-2 refresh 已按 followup runtime 重新刷新
7. `PLAN/STATUS/WORKSET` 已写回 closeout verdict 与 successor routing

说明：

- 本 family 不承诺一定把 phase-2 verdict 推到 `go`
- 但必须把“如何日更 packet / teacher / human label、还差哪些 gate、下一步是否值得重开 review”压成可执行 truth

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `FW1_MULTI_PILOT_RUNTIME_BASELINE` | 把 runtime 从单 pilot candidate path 扩到 small explicit allowlist | allowlist config, runtime baseline artifact, updated candidate/runtime scripts/tests | packet runtime no longer depends on a single pilot service |
| `FW2_TEACHER_THROUGHPUT_AND_BATCH_REVIEW` | 提高 reviewed teacher volume 并保持 hard-case selection 有 provenance | teacher budget/config updates, review batch proof, refreshed ledgers | reviewed teacher growth is measurable and script-backed |
| `FW3_HUMAN_WRITEBACK_AND_LABEL_BACKFILL` | 把 fallback / escalation 样本写回 outcome / training / incident stores | write-back contract, helper tooling/docs, refreshed label/outcome evidence | human-confirmed write-back becomes daily, not ad hoc |
| `FW4_SCHEMA_CHECKPOINT_AND_DAILY_ACCUMULATION` | 把 schema stability 与 accumulation readout 变成日更 checkpoint truth | append-only schema history, refreshed accumulation readout, daily runtime hooks | schema progress and residual gates are measurable over real elapsed days |
| `FW5_PHASE2_RERUN_AND_SUCCESSOR_DECISION` | 基于新 evidence 重新判断是否重开 review | updated phase2 refresh, closeout review, successor admission | honest next step is frozen |

---

## 6. Verification Ladder

### Layer A — slice-local proof

每个 slice 至少补一个 proof-carrying 面：

- fail-first unit test
- script-refreshable artifact
- deterministic json / markdown readout
- `STATUS/WORKSET` writeback

### Layer B — workstream-close proof

每个 workstream closeout 至少补：

- before / after delta against current truth
- refreshed artifact pointers
- gate verdict against followup target, not just predecessor narrative

### Layer C — family-close proof

family closeout 时至少回答：

- runtime packet production 是否已从单 pilot candidate path 扩成 bounded multi-pilot allowlist
- reviewed teacher volume 是否继续增长，且不靠 fake labels
- human-confirmed write-back 是否开始稳定回流
- schema stability 是否进入真实日更窗口
- 当前是否值得重开 `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`

### Default command ladder

- targeted tests for active slice
- `python3 scripts/run_hardening_pipeline.py`
- `python3 scripts/run_data_teacher_accumulation.py`
- `python3 -m unittest discover -s tests -v`

---

## 7. Risks / Blockers

1. multi-pilot runtime 扩展可能滑向无界 observability export
2. 为追赶 teacher volume 可能诱导低质量或无 provenance review
3. human write-back 若没有明确 contract，容易出现 ledger 与 outcome store 脱节
4. schema stability 需要真实时间流逝，不能通过 backfill days 假装完成
5. local small model creep 可能把 family 目标从 accumulation followup 拉偏成 premature implementation

---

## 8. Stop Conditions

遇到以下情况，`execute-plan` 必须停止并回 `plan-creator` 或用户：

- active slice 需要引入 local small model runtime 才能继续
- active slice 需要全服务无界 observability export 才能继续
- teacher / human label provenance 无法保持
- schema checkpoint 只能靠 backdating 或伪造 elapsed days 才能“过门槛”
- 当前 workset 出现多个 equally-primary 下一刀，无法安全继续单 slice 执行

---

## 9. Successor Admission

本 family closeout 后允许的 successor 方向：

1. `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`
   - 当 teacher volume、schema stability、human write-back 与 deployment-readiness evidence 已实质改善
2. another bounded accumulation residual family
   - 当 followup runtime 已落地，但真实时间窗 / reviewed volume / label alignment 仍不足

当前默认不允许直接进入：

- `LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION`

除非 closeout 时有新的明确 review truth 覆盖当前 `not-yet` 判定。

---

## 10. Initial Ordering

默认执行顺序：

1. `FW1.S1_MULTI_PILOT_ALLOWLIST_AND_DAILY_RUNTIME_BASELINE`
2. `FW2.S1_TEACHER_THROUGHPUT_AND_DAILY_REVIEW_BATCH`
3. `FW3.S1_HUMAN_WRITEBACK_AND_LABEL_BACKFILL_CONTRACT`
4. `FW4.S1_APPEND_ONLY_SCHEMA_CHECKPOINT_AND_ACCUMULATION_REFRESH`
5. `FW5.S1_PHASE2_RERUN_AND_SUCCESSOR_DECISION`

只有当 `FW1` 证明 runtime 不再被单 pilot candidate path 卡住后，才允许进入 `FW2`。

---

## 11. Closeout Note

本 family 已完成 closeout，当前 frozen outcome：

- runtime allowlist landed and remains bounded multi-pilot
- reviewed teacher lane advanced to `selected=3 / reviewed=3 / fallback=0`
- reviewed packet write-back is explicit and fully audited for the current reviewed lane
- schema history now preserves append-only checkpoints
- refreshed followup verdict remains `not-yet`
- recommended successor = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL`
