# LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_READINESS_RUBRIC

- Family: `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- Status: frozen-for-closeout
- Last verified: 2026-04-16

## Verdict Standards

- `go`
  - readiness criteria 全部满足，或只有非阻断 partial 项
- `not-yet`
  - 路线仍成立，但存在阻断 implementation 的 readiness 缺口
- `no-go`
  - 当前 evidence 显示 small-model implementation 不是下一步正确动作，或 ROI 不成立

## Criteria

### 1. `schema_stability_2_to_4_weeks`

Question:

- packet/schema surface 是否已稳定足够长时间，值得进入本地小模型实施周期

Go bar:

- `schema stability >= 14 days`
- 没有 active schema churn family

### 2. `teacher_judgement_volume_sufficient`

Question:

- reviewed teacher / human judgement 数量是否足以支撑 distillation/tuning

Go bar:

- reviewed teacher cases `>= 10`
- fallback ratio `<= 0.2`

### 3. `baseline_recall_ceiling_clear`

Question:

- replay / calibration artifacts 是否已经说明 baseline 在哪里开始到顶

Go bar:

- expanded replay coverage
- calibration artifact 已存在
- 剩余 recall / precision 痛点可明确描述

### 4. `hard_cases_are_small_model_worthy`

Question:

- 当前剩余 hard cases 是否主要是 small model 值得解决的语义问题，而不是 review/data gap

Go bar:

- semantic failures 明显多于 review-gap
- 且影响 severe / top-ranked cases

### 5. `local_budget_latency_and_rollback_ready`

Question:

- budget / latency / deployment / rollback 约束是否已足够明确，可以进入 implementation family

Go bar:

- budget defined
- latency bar defined
- rollback path defined
- offline/online success bar frozen

## Non-goals

- 在当前 family 直接训练 small model
- 在当前 family 直接替换 baseline student
- 在当前 family 推进 production auto-action
