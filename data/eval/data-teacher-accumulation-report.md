# Data and Teacher Accumulation Baseline

## Predecessor Readback
- predecessor family: `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- predecessor verdict: `not-yet`
- recommended successor: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION`
- predecessor reason: Current blockers are still dominated by replay breadth, teacher volume, and review-gap evidence rather than semantic model failure.
- phase-2 summary: `{'met': 0, 'partial': 1, 'unmet': 4}`

## Current Baseline
- pilot service count: `2`
- coverage services: `['g-crm-campaign', 'prod-hq-bff-service']`
- replay dataset count: `9`
- replay output row total: `64`
- teacher request count: `2`
- teacher reviewed count: `1`
- teacher fallback count: `1`
- teacher fallback ratio: `0.5`
- queue summary consistent: `True`
- label sources: `{'human_outcome': 4, 'production_outcome': 3, 'teacher_rubric': 1, 'rule': 2}`
- schema stability days: `0`
- severe recall: `1.0`
- top-K precision: `1.0`

## Target Gaps by Workstream
- `DW1.S1_MULTI_PILOT_REPLAY_COVERAGE_EXPANSION` :: expand bounded replay evidence beyond the single current pilot
  - pilot service count `2` -> `2` (gap `0`)
- `DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION` :: grow reviewed teacher volume and keep label-source mix moving with provenance
  - teacher reviewed count `1` -> `10` (gap `9`)
  - teacher fallback ratio `0.5` <= `0.2` (gap `0.3`)
  - teacher rubric label growth needed: `True` from current `1`
- `DW3.S1_SCHEMA_STABILITY_HISTORY_AND_PHASE2_REFRESH` :: track schema stability over time and re-evaluate phase-2 readiness with refreshed evidence
  - schema stability days `0` -> `14` (gap `14`)
  - readiness refresh preconditions: `['multi-pilot replay evidence exceeds 1 bounded pilot', 'reviewed teacher volume materially exceeds predecessor baseline', 'schema fingerprint history has at least one persisted checkpoint']`

## Suggested Execution Order
- recommended next slice: `DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION`
- `DW1.S1_MULTI_PILOT_REPLAY_COVERAGE_EXPANSION`
- `DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION`
- `DW3.S1_SCHEMA_STABILITY_HISTORY_AND_PHASE2_REFRESH`
