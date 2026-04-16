# LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_STATUS

- Family: `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- Status: active
- Refresh verdict: `handoff-to-execute-plan`
- Current phase: `RW0_REVIEW_RUBRIC_FREEZE`
- Active slice: `RW0.S1_READINESS_RUBRIC_AND_EVIDENCE_LEDGER_FREEZE`
- Current branch: `main`
- Last updated: 2026-04-16

---

## 1. Current Truth

- predecessor `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING` 已 closeout
- 当前 repo 已具备 small-model review 的前置 evidence surfaces：
  - `data/samples/replay-pack-manifest.json`
  - `data/eval/label-ledger.json`
  - `data/eval/calibration-report.json`
  - `data/eval/teacher-request-ledger.jsonl`
  - `data/eval/teacher-review-ledger.jsonl`
  - `data/eval/teacher-fallback-ledger.jsonl`
  - `data/eval/control-plane-live-readback.json`
  - `data/eval/enrichment-usage.json`
  - `data/reports/daily-shadow-report.md`
- `docs/mvp/alert-intelligence-mvp.md` 第 12 节已明确 local small model 升级条件

## 2. Current Step

当前第一刀不是评估具体模型名字，也不是开始训练。

当前第一刀应先冻结 review rubric 和 evidence ledger，明确：

- 我们要回答哪些 readiness 问题
- 每个问题对应哪些已有证据
- 哪些缺口会阻断 `go`

## 3. Next Step

由 `execute-plan` 执行 `RW0.S1_READINESS_RUBRIC_AND_EVIDENCE_LEDGER_FREEZE`：

1. 产出 small-model readiness rubric 文档
2. 产出 evidence ledger / condition matrix
3. 明确 `go / no-go / not-yet` 三种 verdict 的判定标准
4. 将 closeout 写回 `STATUS/WORKSET`

## 4. Blockers / Open Decisions

### Open, but not blocking pack creation

- 候选 local model families 是偏 encoder 还是小 instruct model，尚未比较
- budget / latency 的具体硬数值阈值尚未冻结
- 当前 review 是只看单 pilot family，还是要求至少再看一轮 replay expansion，尚未定

### Blocking later workstreams if unresolved

- `RW1` 前必须冻结 readiness rubric
- `RW2` 前必须明确 hard-case taxonomy 的分类标准
- `RW3` 前必须明确 success bar 和 rollback bar 的表达方式

## 5. Gate State

| Gate | State | Notes |
|---|---|---|
| predecessor closeout exists | green | hardening family closed honestly |
| successor plan exists | green | review pack created |
| readiness rubric exists | red | not started |
| evidence ledger exists | red | not started |
| model option matrix exists | red | not started |
| deployment/rollback review exists | red | not started |

## 6. Latest Evidence

- `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_CLOSEOUT_REVIEW.md`
- `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_SUCCESSOR_ADMISSION.md`
- workspace clean on `main`
- current repo has no active implementation family after hardening closeout

## 7. Risks

1. 若不先冻结 rubric，后续 review 会流于“凭感觉觉得差不多可以上小模型”
2. 若不把 evidence ledger 明确化，Phase-2 条件会再次退化为 narrative judgement
3. 若 review family 滑向模型实现，会破坏本 family 的 honest decision boundary

## 8. Closeout Expectation For Current Slice

`RW0.S1` closeout 时至少应写明：

- readiness rubric 放在哪
- evidence ledger 放在哪
- `go / no-go / not-yet` 的判定标准是什么
- 下一刀是否可安全进入 `RW1_EVIDENCE_AUDIT`
