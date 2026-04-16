# Local Small Model Student Upgrade Review

## Readiness Rubric
- `schema_stability_2_to_4_weeks`: Has the packet/schema surface remained stable long enough to justify a local model implementation cycle?
- `teacher_judgement_volume_sufficient`: Is there enough reviewed teacher/human judgement volume to support distillation or tuning?
- `baseline_recall_ceiling_clear`: Do replay/calibration artifacts show where the current baseline plateaus?
- `hard_cases_are_small_model_worthy`: Are the remaining hard cases primarily semantic understanding problems rather than review/data gaps?
- `local_budget_latency_and_rollback_ready`: Are budget, latency, deployment, and rollback constraints explicit enough for implementation?

## Evidence Ledger
- schema stability days: `0`
- replay dataset count: `9`
- teacher reviewed count: `1`
- teacher fallback count: `1`
- outcome total: `8`
- severe recall: `1.0`
- top-K precision: `1.0`

## Phase-2 Condition Audit
- `schema_stability_2_to_4_weeks` => `unmet` :: schema stability days=0 < 14
- `teacher_judgement_volume_sufficient` => `unmet` :: reviewed=1 fallback=1 selected=2
- `baseline_recall_ceiling_clear` => `partial` :: expanded replay and calibration exist, but evidence remains single-pilot
- `hard_cases_are_small_model_worthy` => `unmet` :: dominant_gap=review_gap semantic_failure_count=0
- `local_budget_latency_and_rollback_ready` => `unmet` :: local model budget not frozen; latency budget not frozen; rollback plan not frozen

## Hard-case Taxonomy
- review gap count: `1`
- semantic failure count: `0`
- dominant gap: `review_gap`

## Model Option Matrix
- `keep_classic_baseline` `preferred_now` risk=`low` :: Current baseline already achieves severe_recall=1.0 on the bounded pilot and remaining hard cases are dominated by review/data gaps.
- `small_encoder_classifier` `future_candidate` risk=`medium` :: Future candidate if replay coverage and reviewed teacher volume materially increase.
- `small_instruct_reranker` `defer` risk=`high` :: Would add deployment and latency complexity before the repo has enough evidence that semantic failures dominate.

## Deployment and Guardrails
- deployment readiness: `not_ready`
- blocker: local model budget not frozen
- blocker: latency budget not frozen
- blocker: rollback plan not frozen

## Acceptance and Rollback Bars
- success recall floor: `1.0`
- success top-K precision floor: `1.0`
- success teacher escalation ceiling: `0.15`
- rollback recall trigger: `1.0`
- rollback precision trigger: `0.95`
- rollback fallback rate ceiling: `0.5`

## Final Verdict
- verdict: `not-yet`
- recommended successor: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
- reason: Current blockers are still dominated by replay breadth, teacher volume, and review-gap evidence rather than semantic model failure.
