# LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_PLAN

- Status: active
- Family: `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- Created: 2026-04-16
- Plan type: repo-global successor review pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING`
- Source anchors:
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/mvp/alert-intelligence-mvp.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_SUCCESSOR_ADMISSION.md`
  - `AGENTS.md`

---

## 1. Goal

对“是否进入本地小模型 student 实施”做 evidence-driven readiness review，而不是直接上模型实现。

本 family 的目标是回答：

- 当前 replay coverage、label quality、teacher workflow 是否足以支撑 local small model 路线
- 当前 hard cases 是否真的主要卡在跨模板/跨信号语义理解，而不是还卡在数据和流程层
- 当前预算、延迟、部署、回退与 success bar 是否已经清楚到可以进入实施 family

本 family 的边界是：

> 输出一个 honest `go / no-go / not-yet` verdict，并给出下一 family admission；不在本 family 内直接训练或上线本地小模型 student。

---

## 2. Scope

## 2.1 In scope

- small-model readiness rubric
- replay / label / teacher / calibration evidence audit
- hard-case gap review：当前 baseline 真正失分点分类
- candidate local model families review：small encoder / small instruct model / keep classic model baseline
- budget / latency / deployment / rollback review
- evaluation bar / acceptance gate / rollout guardrail freeze
- final successor admission

## 2.2 Out of scope

- 本地小模型训练或蒸馏实施
- 新 production action sink
- 多 service full rollout
- 新 observability platform product化
- 外部 heavy infra 引入

---

## 3. Entry Criteria

以下前置已满足：

- `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION` 已 closeout
- `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING` 已 closeout
- 当前已有：
  - replay manifest + replay policy
  - retrieval index + compat readout
  - label ledger + calibration report
  - teacher request/review/fallback ledgers
  - live enrichment fallback telemetry
  - hardened shadow report
- `docs/mvp/alert-intelligence-mvp.md` 已明确 Phase-2 upgrade conditions

---

## 4. Family Exit Criteria

当以下条件同时满足时，本 family 可 closeout：

1. local small model readiness rubric 已冻结
2. replay / label / teacher / calibration 证据已对照 rubric 完成审计
3. 当前 hard cases 是否属于 small-model-worthy gap 已有明确分类
4. local model candidate options 已形成 bounded decision matrix
5. budget / latency / deployment / rollback 约束已形成 artifact
6. evaluation success bar 与 rollback bar 已冻结
7. 已给出 successor admission：
   - `LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION`
   - 或 `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
   - 或 `KEEP_BASELINE_STUDENT_AND_CONTINUE_HARDENING`
8. `PLAN/STATUS/WORKSET` 已写回 closeout verdict 与 successor recommendation

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `RW0_REVIEW_RUBRIC_FREEZE` | 冻结 readiness rubric、review question set 与 non-goals | rubric doc, criteria matrix, review pack scaffold | review standard explicit |
| `RW1_EVIDENCE_AUDIT` | 审计 replay / label / teacher / calibration 是否满足 phase-2 条件 | evidence audit, gap ledger, phase-2 condition readback | each upgrade condition gets evidence-backed verdict |
| `RW2_HARD_CASE_AND_MODEL_OPTION_REVIEW` | 审查当前 hard cases 与 candidate local model families 是否匹配 | hard-case taxonomy, option matrix, risk comparison | small-model value proposition is explicit |
| `RW3_DEPLOYMENT_AND_GUARDRAIL_REVIEW` | 收敛预算、延迟、部署、回退、evaluation/rollback bars | deployment review, acceptance gate, rollback plan | implementation family would have real guardrails |
| `RW4_CLOSEOUT_AND_SUCCESSOR_ADMISSION` | 冻结 final go/no-go/not-yet 结论与 successor admission | closeout review, successor recommendation | honest next-family decision frozen |

---

## 6. Verification Ladder

### Layer A — slice-local proof

每个 slice 至少要有一个最小证明面：

- docs matrix / criteria table
- evidence readback against existing artifacts
- targeted review note or diff table
- option matrix / risk table

### Layer B — workstream-close proof

workstream closeout 时至少补：

- audited evidence pointers
- explicit verdict per review question
- `STATUS/WORKSET` closeout writeback

### Layer C — family-close proof

family closeout 时至少回答：

- 当前 repo 是否真的 ready to enter local small model implementation
- 若不 ready，最小阻断项是什么
- 下一 family 应该是什么，而不是什么

---

## 7. Stop Conditions

遇到以下情况，`execute-plan` 必须停止并回 `plan-creator` 或用户：

- review family 开始滑向实际模型实现
- small-model candidate 需要新的平台/审批信息才能继续判断
- readiness rubric 与 MVP phase-2 condition 出现根本冲突
- 当前 evidence 无法支撑 honest verdict，且需要新一轮 hardening family 而不是继续 review

---

## 8. Successor Admission

本 family closeout 后只允许从以下方向中选择 successor：

1. `LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION`
   - 仅当 readiness verdict = `go`
2. `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
   - 当 verdict = `not-yet` 且主要缺口在 data / teacher / replay coverage
3. `KEEP_BASELINE_STUDENT_AND_CONTINUE_HARDENING`
   - 当 verdict = `no-go` 或 small-model ROI 不成立

若 closeout 时三者仍不清晰，不得跳到 implementation。
