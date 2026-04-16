# LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_WORKSET

- Family: `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- Workstream: `RW0_REVIEW_RUBRIC_FREEZE` → `RW4_CLOSEOUT_AND_SUCCESSOR_ADMISSION`
- Active slice count: `1`
- Active slice: `RW0.S1_READINESS_RUBRIC_AND_EVIDENCE_LEDGER_FREEZE`
- Control rule: do not activate the next slice until the current slice has a written closeout verdict

---

## 1. Active Slice Card

### `RW0.S1_READINESS_RUBRIC_AND_EVIDENCE_LEDGER_FREEZE`

- Type: `review + docs`
- Owner neighborhood: `docs/plan + evidence readback`
- Goal:
  - 把 local small model upgrade review 的判断标准先冻结，再进入 evidence audit
- Source anchors:
  - `docs/mvp/alert-intelligence-mvp.md` §12
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_CLOSEOUT_REVIEW.md` §5, §6
  - `docs/architecture/alert-intelligence-architecture.md` §11, §12, §14, §17
- Target artifacts:
  - readiness rubric doc
  - evidence ledger / condition matrix doc
  - closeout writeback in `STATUS/WORKSET`
- Verification shape:
  - rubric questions map to explicit evidence surfaces
  - verdict standards for `go / no-go / not-yet` are scanable and non-overlapping
- Stop condition:
  - 若 review rubric 直接变成实施方案，则停止并回 `plan-creator`
  - 若 Phase-2 condition 需要被重写而不是审计，则停止并升级
- Residual seed:
  - `RW1.S1_PHASE2_CONDITION_AUDIT`
  - `RW2.S1_HARD_CASE_TAXONOMY_AND_MODEL_OPTION_MATRIX`

---

## 2. Ordered Slice Queue

| Slice ID | Type | Owner neighborhood | Target output | Verification | Status | Activation rule | Stop condition |
|---|---|---|---|---|---|---|---|
| `RW0.S1_READINESS_RUBRIC_AND_EVIDENCE_LEDGER_FREEZE` | review/docs | review control plane | readiness rubric + evidence ledger | criteria/evidence mapping is explicit | active | active immediately | stop if review becomes implementation planning |
| `RW1.S1_PHASE2_CONDITION_AUDIT` | audit | evidence surfaces | per-condition verdict table against MVP §12 | every phase-2 condition gets `met / partial / unmet` | planned | activate after `RW0.S1` closeout green | stop if evidence set is insufficient for honest condition verdict |
| `RW1.S2_BLOCKER_AND_GAP_LEDGER` | audit/replan | gap control | blocker ledger + gap taxonomy | blockers classified into data / label / teacher / infra / ROI | planned | activate after `RW1.S1` lands | stop if blocker set implies a different family is needed immediately |
| `RW2.S1_HARD_CASE_TAXONOMY_AND_MODEL_OPTION_MATRIX` | review/modeling | option review | hard-case taxonomy + model option matrix | small-model value proposition is explicit | planned | activate after `RW1.S2` closeout | stop if small-model candidates cannot be compared within current evidence |
| `RW3.S1_BUDGET_LATENCY_DEPLOYMENT_REVIEW` | ops/review | rollout guardrail | budget/latency/deployment/rollback review | implementation constraints are explicit | planned | activate after `RW2.S1` lands | stop if external approval or missing infra blocks honest review |
| `RW3.S2_SUCCESS_BAR_AND_ROLLBACK_BAR_FREEZE` | review/docs | acceptance gate | success bar + rollback bar + eval gate | future implementation family would have measurable guardrails | planned | activate after `RW3.S1` closeout | stop if success bar still depends on missing evidence |
| `RW4.S1_FINAL_VERDICT_AND_SUCCESSOR_ADMISSION` | closeout | repo-global | final go/no-go/not-yet verdict + successor recommendation | closeout review and successor recommendation written | planned | activate after `RW3.S2` lands | stop if successor direction still ambiguous |

---

## 3. Residual Seed Pool

这些项现在不激活，但在 closeout 时必须判断是否升级为下一 family：

- local small model implementation pack
- further data / teacher accumulation pack
- keep-baseline decision pack with guardrail refresh

---

## 4. Workset Hygiene Rules

- 同时只能有一个 `active` slice
- `done` 只在 matching verification 跑过后写入
- closeout 未写回前，不得切到下一刀
- 如果 queue 中下一刀不再清晰，停止 `execute-plan`，回 `plan-creator`
- 不把 residual pool 当作 active queue
