# fixit Plan Packs

## No Active Family

当前 `docs/plan/` 中的两个 family 都已 closeout。

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

当前 `docs/plan/` 承载两段已经完成的连续目标：

- predecessor `foundation`：证明 MVP shadow foundation 能跑通并已完成 closeout。
- current `hardening`：把 foundation 的 replay / retrieval / calibration / teacher / enrichment 残口压成新的 bounded successor，并已完成 closeout。

## Read Order

1. 先读 `..._PLAN.md`：理解 bounded family、scope、workstreams、exit gate。
2. 再读 `..._STATUS.md`：理解 current truth、active slice、blockers、next step。
3. 最后读 `..._WORKSET.md`：按单一 active slice 推进，不要跳行并行扩 scope。

## Control Rule

- 当前没有 active family。
- closed families 不得继续续写。
- 若继续下一阶段，默认先回 `plan-creator`，为 `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW` 建新 pack。
