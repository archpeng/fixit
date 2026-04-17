# fixit Plan Packs

## No Active Execute Family

- temporal P7 family is closed
- temporal successor ladder currently collapses at P7 on current evidence
- alert-intelligence daily residual lane remains blocked by real next-date progression

## Blocked Current Family

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL_PLAN.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL_STATUS.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL_WORKSET.md`
  - current resume gate: wait for the next real distinct date before `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT`

## Closed Current Family

- `TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT`
  - `docs/plan/TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT_PLAN.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT_STATUS.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT_WORKSET.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT_SUCCESSOR_ADMISSION.md`
  - ladder outcome: `collapse_temporal_ladder_here`

## Closed Previous Family

- `TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT`
  - `docs/plan/TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_PLAN.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_STATUS.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_WORKSET.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_CLOSEOUT_REVIEW.md`
  - `docs/plan/TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_SUCCESSOR_ADMISSION.md`

## Purpose

当前 `docs/plan/` 承载：

1. 一个被真实日期阻塞的 alert-intelligence daily residual family
2. 已闭合到 P7 的 temporal family 链路
3. 一个在当前证据下已于 P7 收束的 temporal successor ladder

## Control Rule

- 当前没有 active execute family。
- blocked family 只能在其真实外部 gate 满足后恢复。
- temporal ladder 不得自动继续到 P8；当前 truth 是 `collapse_temporal_ladder_here`。
- 若未来重新打开 temporal continuation，必须先有新的 evidence surface。
