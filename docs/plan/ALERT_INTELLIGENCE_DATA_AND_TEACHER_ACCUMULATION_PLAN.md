# ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_PLAN

- Status: completed
- Family: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
- Created: 2026-04-16
- Plan type: repo-global successor execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- Source anchors:
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/mvp/alert-intelligence-mvp.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_CLOSEOUT_REVIEW.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_SUCCESSOR_ADMISSION.md`
  - `AGENTS.md`

---

## 1. Goal

把 predecessor review family 判定出的 `not-yet` 阻断项，压成一个可执行、可累积证据、可 honest closeout 的实现 family。

本 family 的目标不是“继续讨论要不要上小模型”，而是实做以下积累面：

- replay breadth
- multi-pilot evidence
- reviewed teacher volume
- label / outcome source mix
- schema stability tracking
- phase-2 readiness refresh inputs

边界是：

> 在不启动 local small model implementation 的前提下，把“数据、teacher、覆盖度、稳定性”这四类缺口尽可能压成脚本化 artifact、tests 和 bounded evidence。

---

## 2. Scope

## 2.1 In scope

- accumulation baseline / target ledger tooling
- multi-pilot replay coverage expansion
- teacher reviewed batch expansion and ledger refresh
- label source mix / outcome coverage refresh
- schema stability history tracker
- updated phase-2 readiness refresh artifact
- closeout verdict + successor recommendation

## 2.2 Out of scope

- local small model training / distillation / serving
- production auto-action
- unbounded observability export
- new UI / dashboard productization
- 把 synthetic 或无 provenance judgement 冒充真实 teacher / human evidence

---

## 3. Entry Criteria

以下前置已满足：

- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW` 已 closeout
- predecessor final verdict = `not-yet`
- predecessor successor admission = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
- 当前已知阻断：
  - `schema_stability_days = 0`
  - `pilot_service_count = 1`
  - `teacher_reviewed_count = 1`
  - `teacher_fallback_count = 1`
  - 当前 hard-case dominant gap = `review_gap`
- 当前 repo 已有可复用 surface：
  - replay pack + manifest refresh
  - teacher workflow + ledgers
  - label ledger + calibration report
  - local small model review module + verdict artifacts

---

## 4. Family Exit Criteria

当以下条件同时满足时，本 family 可 closeout：

1. accumulation baseline / target report 已存在，且可脚本刷新
2. replay coverage artifact 已显式体现 `> 1` bounded pilot / service family 的 coverage
3. reviewed teacher volume 已高于 predecessor baseline，并有 refreshed teacher / label ledgers 支撑
4. schema stability history artifact 已能记录 packet/schema fingerprint 与 elapsed days
5. phase-2 readiness refresh artifact 已用新 evidence 重算关键门槛
6. `PLAN/STATUS/WORKSET` 已写回 closeout verdict 与 residual routing
7. 已明确 successor admission：
   - `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`
   - 或 `LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION`
   - 或 `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`

说明：

- 本 family 不承诺一定达到 small-model `go`
- 但必须把“继续积累什么、已积累多少、何时值得重开 review”压成可执行 truth

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `DW0_BASELINE_AND_TARGET_FREEZE` | 冻结 accumulation baseline、target ledger 与 target gaps | accumulation module, baseline json/md, tests | next slices no longer rely on hidden judgement |
| `DW0 closeout note` | 当前已完成 | `fixit_ai/data_teacher_accumulation.py`, `scripts/run_data_teacher_accumulation.py`, `tests/test_data_teacher_accumulation.py`, `data/eval/data-teacher-accumulation-{baseline,report}` | DW1 admission frozen |
| `DW1_MULTI_PILOT_REPLAY_EXPANSION` | 把 replay pack 从单 pilot 扩到 multi-pilot evidence | replay config/code updates, coverage report, refreshed manifest | coverage gap is explicit and script-backed |
| `DW2_TEACHER_AND_LABEL_ACCUMULATION` | 增加 reviewed teacher / label source evidence | refreshed teacher fixtures/ledgers, label-source report | reviewed teacher growth is measurable |
| `DW3_SCHEMA_STABILITY_AND_READINESS_REFRESH` | 建 schema stability history，并重算 phase-2 inputs | schema fingerprint history, readiness refresh artifact | time-based and evidence-based gates are explicit |
| `DW4_CLOSEOUT_AND_SUCCESSOR_ADMISSION` | 冻结 residuals 与下一 family 选择 | closeout review, successor admission | honest next step frozen |

---

## 6. Verification Ladder

### Layer A — slice-local proof

每个 slice 至少要有一个最小 proof-carrying 面：

- fail-first unit test
- script-refreshable artifact
- deterministic json / markdown readout
- `STATUS/WORKSET` writeback

### Layer B — workstream-close proof

每个 workstream closeout 至少补：

- refreshed evidence artifact pointers
- explicit before/after delta
- gate verdict against predecessor baseline

### Layer C — family-close proof

family closeout 时至少回答：

- replay breadth 是否已超出单 pilot
- reviewed teacher volume 是否已显著高于 predecessor baseline
- schema stability 是否开始进入可追踪窗口
- 当前是否值得重开 small-model review，或继续 accumulation

---

## 7. Stop Conditions

遇到以下情况，`execute-plan` 必须停止并回 `plan-creator` 或用户：

- accumulation family 开始滑向实际 local small model implementation
- 为了追求 teacher volume 开始伪造无 provenance judgement
- second pilot / extra evidence 需要无界 observability 扫描才能继续
- packet/schema surface 发生新一轮重大 churn，导致 stability tracker 与旧 artifact 失真

---

## 8. Successor Admission

本 family closeout 后只允许从以下方向中选择 successor：

1. `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`
   - 当 evidence 已实质变化，但还需再次以 review verdict 冻结结论
2. `LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION`
   - 仅当 refreshed phase-2 conditions 全部满足
3. `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`
   - 当 evidence 有增长，但时间窗 / reviewed volume / coverage 仍不足

若 closeout 时三者仍不清晰，不得跳到 implementation。

---

## 9. Closeout Note

本 family 已完成 closeout，当前 frozen outcome：

- replay breadth improved to multi-pilot
- reviewed teacher batch exceeds predecessor baseline
- schema history artifact exists
- refreshed phase-2 verdict remains `not-yet`
- recommended successor = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`
