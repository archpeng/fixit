# fixit Plan Packs

## No Active Family

当前 `docs/plan/` 中的所有 family 都已 closeout。

## Closed Current Family

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_PLAN.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_STATUS.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_WORKSET.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_SUCCESSOR_ADMISSION.md`

## Closed Previous Family

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_PLAN.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_STATUS.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_WORKSET.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_SUCCESSOR_ADMISSION.md`

## Closed Previous Family

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_PLAN.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STATUS.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_WORKSET.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_SUCCESSOR_ADMISSION.md`

## Closed Previous Family

- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_PLAN.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_STATUS.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_WORKSET.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_READINESS_RUBRIC.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_EVIDENCE_AUDIT.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_MODEL_OPTION_MATRIX.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_DEPLOYMENT_REVIEW.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_CLOSEOUT_REVIEW.md`
  - `docs/plan/LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_SUCCESSOR_ADMISSION.md`

## Closed Previous Family

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

当前 `docs/plan/` 承载六段已经完成的连续目标：

- closed `data-and-teacher-accumulation-stability-and-volume-residual`：围绕 residual truth 收口 reviewed teacher volume ceiling、bounded packet supply、schema distinct-day progress、family recheck 与 successor routing。
- closed `data-and-teacher-accumulation-followup`：把下一阶段推荐运行架构压成可执行 runtime family，并完成 allowlist runtime、teacher throughput、write-back audit、append-only schema checkpoint 与 closeout。
- predecessor `foundation`：证明 MVP shadow foundation 能跑通并已完成 closeout。
- closed `hardening`：把 foundation 的 replay / retrieval / calibration / teacher / enrichment 残口压成新的 bounded successor，并已完成 closeout。
- closed `small-model-upgrade-review`：对“是否进入本地小模型 student 实施”完成 readiness review，并给出 `not-yet` verdict。
- closed `data-and-teacher-accumulation`：把 replay breadth / reviewed teacher volume / schema stability / multi-pilot evidence 压成真实代码、tests 和 artifacts，并给出 followup successor。

## Read Order

1. 先读 `..._PLAN.md`：理解 bounded family、scope、workstreams、exit gate。
2. 再读 `..._STATUS.md`：理解 current truth、active slice、blockers、next step。
3. 最后读 `..._WORKSET.md`：按单一 active slice 推进，不要跳行并行扩 scope。

## Control Rule

- 当前没有 active family。
- closed families 不得继续续写。
- 若继续下一阶段，默认先回 `plan-creator`，为 `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL` 建新 pack。
