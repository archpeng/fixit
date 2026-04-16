# fixit Plan Packs

## Current Family

- `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PLAN.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_STATUS.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_WORKSET.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PILOT_ADMISSION.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_CLOSEOUT_REVIEW.md`

## Purpose

当前 `docs/plan/` 只承载一个目标：

- 把 `docs/mvp/alert-intelligence-mvp.md` 里的 MVP 方案压成可续跑、可 closeout、可 handoff 的 `PLAN/STATUS/WORKSET` 控制面。

## Read Order

1. 先读 `..._PLAN.md`：理解 bounded family、scope、workstreams、exit gate。
2. 再读 `..._STATUS.md`：理解 current truth、active slice、blockers、next step。
3. 最后读 `..._WORKSET.md`：按单一 active slice 推进，不要跳行并行扩 scope。

## Control Rule

- 当前 family 已 closeout。
- 若继续下一阶段，默认先回 `plan-creator`，不要在 closed family 上继续追加 successor 工作。
