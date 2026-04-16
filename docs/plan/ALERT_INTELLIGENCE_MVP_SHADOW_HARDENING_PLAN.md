# ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_PLAN

- Status: completed
- Family: `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING`
- Created: 2026-04-16
- Plan type: repo-global successor execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION`
- Source anchors:
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/mvp/alert-intelligence-mvp.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_STATUS.md`
  - `AGENTS.md`

---

## 1. Goal

把已经跑通的 `MVP shadow foundation`，进一步硬化成一个**可重复回放、可解释校准、可审计 teacher、可优先 live enrichment 但有 fallback** 的 bounded pilot lane。

本 family 的目标不是再证明“概念成立”，而是把 foundation 中仍然脆弱的地方收紧：

- replay pack 不再只是一次性样本堆
- retrieval 不再只依赖最小 `jsonl` incident list
- calibration / label hierarchy 有更强证据
- teacher lane 不再只靠 seed judgement
- control-plane enrichment 进入 `live-first with config fallback` 主路径

本 family 的边界是：

> 在不进入本地小模型 student 升级的前提下，把当前 pilot service family 的 shadow lane 从 foundation 升级到 hardening-ready state。

---

## 2. Scope

## 2.1 In scope

- replay pack manifest / refresh tooling / dataset policy
- richer retrieval index or structured local retrieval store hardening
- larger replay window and calibration artifact expansion
- label ledger / source weighting hardening
- teacher request ledger / review fallback / auditability hardening
- control-plane live enrichment path with explicit fallback to local config
- hardening-level shadow report additions：data freshness、fallback usage、review queue visibility
- successor admission for either:
  - `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
  - or `MVP_SHADOW_PRODUCTION_PILOT_HARDENING`

## 2.2 Out of scope

- 本地小 LLM student 实施
- production auto-action / auto-remediation
- 全服务 rollout
- full observability productization
- external vector database or heavy infra rollout if local hardening is sufficient

---

## 3. Entry Criteria

以下前置已满足：

- predecessor family `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION` 已 closeout
- `python3 -m unittest discover -s tests -v` 曾通过
- `python3 scripts/run_shadow_pipeline.py` 曾成功跑通
- current pilot family 已冻结：`g-crm-campaign / ADCService/Compile / 24h`
- current residuals 已明确记录于 predecessor closeout

---

## 4. Family Exit Criteria

当以下条件同时满足时，本 family 可 closeout：

1. replay pack manifest 与 refresh policy 已冻结，且能说明哪些输入来自 live bounded export、哪些来自 retained fixture
2. 至少一轮扩展 replay pack 能在固定 manifest 下稳定重建或刷新
3. retrieval store/index 已从最小原型升级到 hardening-ready 形态，并保留 explainable refs
4. calibration artifact 已基于更大 replay coverage 输出，并能解释阈值调整或维持不调的原因
5. label ledger / source weighting 已从 narrative 变成可执行 artifact
6. teacher request/review/fallback 路径已具备 ledger 与 audit surface
7. control-plane enrichment 已支持 `live-first`，并在失败时显式回落到 config fallback
8. shadow report 已增加 hardening signals：data freshness、fallback usage、teacher queue visibility
9. `PLAN/STATUS/WORKSET` 已写回 closeout verdict 与 successor admission
10. `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING_CLOSEOUT_REVIEW.md` 已固定本 family 的 hardening evidence 与 residuals

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `HW0_REPLAY_BOUNDARY_FREEZE` | 冻结 replay pack contract、refresh tooling、dataset policy | replay manifest, refresh script, policy note, tests | replay pack can be rebuilt or refreshed deterministically |
| `HW1_RETRIEVAL_HARDENING` | 把 retrieval 从最小 incident list 升级到 hardening-ready local store/index | retrieval store/index, explainable refs, compatibility readout | retrieval remains explainable and survives larger replay set |
| `HW2_CALIBRATION_AND_LABEL_HARDENING` | 扩大 replay coverage、固化 label ledger 和 calibration artifact | replay expansion, label ledger, calibration summary | threshold stance can be defended with artifact evidence |
| `HW3_TEACHER_WORKFLOW_HARDENING` | 让 teacher lane 具备 request/review ledger、fallback 和审计面 | request ledger, review ledger, fallback policy | teacher lane no longer depends on hidden seed judgement semantics |
| `HW4_LIVE_ENRICHMENT_HARDENING` | 控制 topology/owner/repo enrichment 优先 live control-plane，保留 config fallback | live enrichment adapter, fallback evidence, usage telemetry | enrichment path explicit and auditable |
| `HW5_CLOSEOUT_AND_SUCCESSOR_ADMISSION` | 汇总 hardening evidence，决定下一阶段 admission | closeout review, successor recommendation | family exit criteria checked and frozen |

---

## 6. Verification Ladder

### Layer A — slice-local proof

每个 slice 至少要有一个最小证明面：

- targeted unit test
- deterministic replay rebuild
- schema / manifest validation
- local script smoke
- bounded artifact diff / readout

### Layer B — workstream-close proof

workstream closeout 时至少补：

- updated replay / calibration / review artifacts
- `STATUS/WORKSET` closeout writeback
- current workstream claims vs landed files readback

### Layer C — family-close proof

family closeout 时至少回答：

- replay / retrieval / teacher / live enrichment 是否都比 predecessor 更 hardening-ready
- 是否足以支撑下一阶段：small-model review 或 production pilot hardening

---

## 7. Stop Conditions

遇到以下情况，`execute-plan` 必须停止并回 `plan-creator` 或用户：

- replay hardening 需要引入超出 repo 当前能力的大型基础设施
- calibration 结论推翻当前 MVP severity semantics
- control-plane live enrichment 在当前环境下无法稳定调用且 fallback 语义不清
- teacher workflow hardening 演变成新产品/平台范围，而非 bounded pilot lane
- successor admission 需要更大的 family split 而不是 continuation

---

## 8. Successor Admission

本 family closeout 后，只允许从以下方向里选择 successor：

1. `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
   - 仅当 calibration、teacher、label、replay 都已足够硬化
2. `MVP_SHADOW_PRODUCTION_PILOT_HARDENING`
   - 若目标转向更真实的 production-facing pilot lane

若 closeout 时这两个 admission 都不清晰，不得跳转到实施 family。
