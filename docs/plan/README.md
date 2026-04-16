# fixit Plan Packs

## Active Family

- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_PLAN.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_STATUS.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_WORKSET.md`

## Closed Current Family

- `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_PLAN.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_STATUS.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_WORKSET.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_REPLAY_POLICY.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_SUCCESSOR_ADMISSION.md`

## Closed Predecessor

- `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PLAN.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_STATUS.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_WORKSET.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PILOT_ADMISSION.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_CLOSEOUT_REVIEW.md`

## Purpose

当前 `docs/plan/` 承载三段连续目标：

- predecessor `foundation`：证明 MVP shadow foundation 能跑通并已完成 closeout。
- closed `hardening`：把 foundation 的 replay / retrieval / calibration / teacher / enrichment 残口压成新的 bounded successor，并已完成 closeout。
- active `small-model-upgrade-review`：对“是否进入本地小模型 student 实施”做 readiness review，而不是直接实施。

## Read Order

1. 先读 `..._PLAN.md`：理解 bounded family、scope、workstreams、exit gate。
2. 再读 `..._STATUS.md`：理解 current truth、active slice、blockers、next step。
3. 最后读 `..._WORKSET.md`：按单一 active slice 推进，不要跳行并行扩 scope。

## Control Rule

- 当前 active family 默认 handoff 给 `execute-plan`。
- closed families 不得继续续写。
- 若当前 review family 的下一刀不清晰、verification ladder 变化、或 successor scope 需要重拆，回到 `plan-creator`。
