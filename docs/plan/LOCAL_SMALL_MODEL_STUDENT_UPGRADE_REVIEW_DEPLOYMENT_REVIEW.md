# LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_DEPLOYMENT_REVIEW

- Family: `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- Status: frozen-for-closeout
- Last verified: 2026-04-16

## Deployment Readiness

- deployment readiness: `not_ready`

Current blockers:

- local model budget not frozen
- latency budget not frozen
- rollback plan not frozen

## Acceptance Bars

- success recall floor: `1.0`
- success top-K precision floor: `1.0`
- success teacher escalation ceiling: `0.15`

Interpretation:

- future implementation family 至少要在 bounded replay 上不劣于当前 baseline
- 不允许用更高 teacher/fallback 负担换取“看起来更聪明”的局部提升

## Rollback Bars

- rollback recall trigger: `1.0`
- rollback precision trigger: `0.95`
- rollback fallback rate ceiling: `0.5`

Interpretation:

- implementation family 一旦跌破当前 bounded replay 保护线，就必须支持快速回滚
- 当前仍未定义 latency budget，因此 implementation family 前必须先补这一条
