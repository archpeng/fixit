# ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_STATUS

- Family: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`
- Status: completed
- Refresh verdict: `accept_with_residuals`
- Current phase: `family-closeout`
- Active slice: `none`
- Current branch: `main`
- Last updated: 2026-04-16

---

## 1. Current Truth

当前 family 由 predecessor closeout 直接 admitted，且当前 governing runtime truth 已由：

- `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`

冻结为：

- `incident packet` 继续是 canonical decision unit
- 默认运行面采用 `cheap dense scorer -> teacher hard-case review -> human gate`
- local small model dense first pass 继续延后

当前已知 quantitative truth：

- replay coverage 已覆盖 `2` services：
  - `g-crm-campaign`
  - `prod-hq-bff-service`
- `phase2_verdict = not-yet`
- `current_teacher_reviewed_count = 3`
- `target_teacher_reviewed_count = 10`
- `teacher_label_gap = 0` for the current reviewed lane
- `current_schema_stability_days = 0`
- `target_schema_stability_days = 14`
- `teacher max_reviews_per_run = 3`
- `teacher max_tokens_per_run = 6000`

当前最关键的执行真相是：

- replay evidence 已是 multi-pilot
- runtime candidate path 已切到 small explicit allowlist
- runtime baseline artifact 已证明 runtime 扫描面不再隐式绑定单 pilot service
- teacher volume 仍不足以支持 review rerun
- schema checkpoint 仍只是刚起步，不足以支撑 phase-2 gate

## 2. Active Slice Objective

刚完成 slice：`FW1.S1_MULTI_PILOT_ALLOWLIST_AND_DAILY_RUNTIME_BASELINE`

FW1 closeout evidence：

- `configs/services.yaml` 新增 `runtime_pilot_allowlist`
- `scripts/generate_candidate_windows.py` 改为从 allowlist 解析 runtime 范围
- `fixit_ai/candidate_generation.py` 新增 `resolve_allowed_services(...)`
- `data/eval/data-teacher-runtime-baseline.{json,md}` 已落地
- `python3 scripts/run_hardening_pipeline.py` 产出 `7` candidate windows / `7` packets
- runtime baseline 证明：
  - allowlist services = `['g-crm-campaign', 'prod-hq-bff-service']`
  - observed metric services = `['g-crm-campaign', 'prod-hq-bff-service']`
  - current candidate services = `['g-crm-campaign']`
  - second service 当前未触发 candidate，但 runtime 已纳入扫描面

刚完成 slice：`FW2.S1_TEACHER_THROUGHPUT_AND_DAILY_REVIEW_BATCH`

FW2 closeout evidence：

- `configs/teacher-budget.yaml` 更新为：
  - `max_reviews_per_run = 3`
  - `max_tokens_per_run = 6000`
  - `confidence_below = 0.36`
- `data/eval/manual_teacher_judgements.jsonl` 扩展为 `ipk_w002`, `ipk_w004`, `ipk_w006`
- `data/eval/fixtures/teacher_review_batch.retained.jsonl` 扩展为 `3` reviewed packets
- `data/eval/data-teacher-daily-review-batch.{json,md}` 已落地
- sequential refresh truth：
  - selected = `3`
  - reviewed = `3`
  - fallback = `0`
  - reviewed packet ids = `['ipk_w002', 'ipk_w004', 'ipk_w006']`
- strict review 期间发现并修复一个回归：
  - `fixit_ai.small_model_review.py` 改为优先读取 frozen local-small-model artifacts，避免 predecessor review 被当前 live ledgers 污染

刚完成 slice：`FW3.S1_HUMAN_WRITEBACK_AND_LABEL_BACKFILL_CONTRACT`

FW3 closeout evidence：

- `data/eval/outcomes.jsonl` 已补齐 `ipk_w006` human-confirmed outcome
- `data/eval/training_examples.jsonl` 已补齐 `ipk_w002`, `ipk_w004`, `ipk_w006` packet-linked training backfill
- `data/eval/historical_incidents.jsonl` 已给 `inc-compile-500` / `inc-compile-warmup` 增加 `source_packet_ids`
- `data/eval/data-teacher-human-writeback-audit.{json,md}` 已落地
- `data/eval/data-teacher-review-ledger.json` 现已明确：
  - `training_backfill_count = 3`
  - `teacher_label_gap = 0`
- strict review 期间发现并修复一个评测 drift：
  - `fixit_ai/eval.py` 现在只用当前 run 覆盖到的 packet 计算 severe recall，避免历史 outcome 污染当前 run 的分母

刚完成 slice：`FW4.S1_APPEND_ONLY_SCHEMA_CHECKPOINT_AND_ACCUMULATION_REFRESH`

FW4 closeout evidence：

- `fixit_ai/data_teacher_accumulation.py` 中的 schema history 现在保留 append-only snapshots
- `data/eval/schema-stability-history.json` 当前读数：
  - `snapshot_count = 3`
  - `first_observed_date = 2026-04-17`
  - `current_elapsed_days = 0`

刚完成 slice：`FW5.S1_PHASE2_RERUN_AND_SUCCESSOR_DECISION`

FW5 closeout evidence：

- `data/eval/data-teacher-followup-closeout.{json,md}` 已落地
- `phase2_verdict = not-yet`
- final successor = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL`

当前 family 已完成 closeout，不再有 active slice。

## 3. Gate State

| Gate | State | Notes |
|---|---|---|
| multi-pilot replay evidence exists | green | `pilot_service_count = 2` |
| runtime candidate allowlist is multi-pilot | green | allowlist-driven runtime baseline landed |
| teacher reviewed volume materially above `2` | green | current runtime reviewed count reached `3`; target `10` remains open |
| human write-back contract frozen | green | script-backed write-back audit landed |
| append-only schema checkpoint running | green | append-only checkpoint semantics landed |
| phase-2 rerun admissible | blocked | refreshed verdict still `not-yet` |
| local small model first-pass admission | blocked | not ready per prior review + deployment gates |

## 4. Latest Evidence

### Current evidence anchors

- `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`
- `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_SUCCESSOR_ADMISSION.md`
- `data/eval/data-teacher-runtime-baseline.json`
- `data/eval/data-teacher-daily-review-batch.json`
- `data/eval/data-teacher-human-writeback-audit.json`
- `data/eval/data-teacher-phase2-refresh.json`
- `data/eval/data-teacher-review-ledger.json`
- `data/eval/schema-stability-history.json`
- `data/eval/teacher-queue-summary.json`
- `data/eval/label-ledger.json`

### Inherited validation baseline

Latest verification at family closeout:

```bash
python3 -m unittest tests.test_hardening_pipeline tests.test_data_teacher_accumulation -v
python3 scripts/run_hardening_pipeline.py
python3 scripts/run_data_teacher_accumulation.py
python3 -m unittest discover -s tests -v
```

Result:

- targeted execution tests green
- hardening pipeline green with `selected=3 reviewed=3 fallback=0`
- accumulation refresh green after serial rerun
- full unittest discover green (`31 tests`)

## 5. Risks / Blockers

1. 当前 teacher reviewed count 虽到 `3`，但距离 target `10` 仍远
2. schema stability elapsed days 仍未自然积累到 `14`
3. 直接 `python3 scripts/run_teacher_review.py --seed-judgements data/eval/replay/manual_teacher_judgements.jsonl` 仍会命中治理 false positive；当前安全路径仍是 wrapper/default invocation
4. local small model creep 仍是显式 blocker

## 6. Next Step

默认下一 family：

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL`

若继续执行，下一刀应回 `plan-creator` 建新 pack，而不是继续续写当前 closed family。
