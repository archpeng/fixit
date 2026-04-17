# fixit temporal decision-surface admission ladder

- Status: `proposed-temporal-decision-surface-admission-ladder`
- Scope: `temporal successor ladder after P6 closeout`
- Repo: `/home/peng/dt-git/github/fixit`
- Primary reader: 后续负责创建 `TEMPORAL_ALIGNMENT_P7_*` 及其后续 family 的执行者

---

## 1. Decision Summary

当前 temporal 线允许继续推进，但只允许沿着一条 **条件式 successor ladder** 前进，而不是继续无界扩写 retrieval / prior / fusion 变体。

该 ladder 的目标不是把 temporal 线做成独立产品或 long-sequence model 计划，而是把 temporal 信号从：

- offline alignment / retrieval evidence

推进到：

- bounded trigger policy
- bounded calibration threshold
- bounded teacher / human routing utility
- bounded shadow action policy utility
- 最终是否准入当前 packet-centric runtime 的明确信号

当前冻结的 successor ladder 为：

1. `TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT`
2. `TEMPORAL_ALIGNMENT_P8_QUEUE_ROUTING_UTILITY_AND_BUDGET_COMPARE`
3. `TEMPORAL_ALIGNMENT_P9_SHADOW_ACTION_POLICY_INTEGRATION_COMPARE`
4. `TEMPORAL_ALIGNMENT_P10_RUNTIME_ADMISSION_AND_GUARDRAILS`

该 ladder **不是默认全部执行**；每一阶只有在前一阶 proof bar 满足后才允许创建下一 pack。

---

## 2. Why This Ladder Exists

P6 已冻结的 entry truth：

- `packets_selected_for_hybrid = 5`
- `packets_with_selected_score_delta_gt_raw = 5`
- `packets_with_selected_confidence_delta_gt_raw = 0`
- `folds_with_selective_routing = 3`
- `max_selected_top_score_delta = 0.05`
- `anti_leakage_violation_count = 0`
- major packet / episode metrics remain flat

这意味着：

1. temporal / hybrid 信号已经证明 **对 retrieval score surface 有价值**
2. temporal / hybrid 信号还没有证明 **对 downstream confidence / decision surface 有价值**
3. 如果继续 temporal 方向，下一步就不该再问“还能不能让 retrieval 更聪明一点”，而应转向：
   - 什么时候 temporal score delta 值得影响 trigger policy
   - 什么时候 temporal score delta 值得影响 calibration threshold
   - 什么时候 temporal 信号值得进入 teacher / human / action decision surface

因此，P7 之后必须是“研究面 -> 决策面 -> 运行面”的收敛 ladder，而不是新的开放式 experiment tree。

---

## 3. Temporal End Definition

## 3.1 Admitted end-state

当前 repo 上，temporal 线的合理终点定义为：

> temporal 成为当前 `incident packet -> retrieval -> cheap student -> teacher -> human` 主运行面中的一个 **bounded decision overlay**，并先以 shadow/runtime-admission 形式落地。

这意味着 temporal 的成功终点不是：

- 独立 temporal product
- temporal sidecar production rollout
- long-sequence student backbone
- 替代 packet 为 canonical decision unit

而是：

- 在不改变 canonical unit 的前提下
- 在不破坏 anti-leakage discipline 的前提下
- 在不扩大为无界 review / compute / human load 的前提下
- 让 temporal 信号以有门槛、可回滚、可审计的方式影响当前 runtime 的决策面

## 3.2 Explicit non-endpoints

下列状态**不算** temporal 线终点：

1. 只得到更多 retrieval score delta
2. 只得到更多 prior compaction / fusion artifacts
3. 只能改写 markdown readout，但不能影响 policy / routing
4. 需要把几乎所有 packet 都送入 temporal lane 才能成立
5. 借 temporal 结果暗中绕过 `DV2` schema gate
6. 借 temporal 结果提前重开 local small model implementation

## 3.3 Terminal indicators

只有至少满足以下终态指标，temporal 线才算接近终点：

| Indicator | Meaning |
|---|---|
| `anti_leakage_violation_count = 0` | temporal line remains admission-grade rather than optimistic |
| `packets_with_policy_delta_gt_raw > 0` | temporal signal creates non-empty policy-level differences |
| `folds_with_policy_delta > 0` | policy delta is not a single-packet accident |
| `queue_utility_delta >= 0` | teacher / human queue quality does not degrade |
| `action_policy_delta_count > 0` | temporal signal can affect bounded shadow action decisions |
| `major_metric_regression = false` | packet severe recall / top-K precision / episode precision do not regress |
| `budget_regression = false` | teacher/human cost does not blow up uncontrollably |
| `shadow_runtime_admission` is explicit | final state is either `admit_to_shadow_runtime` or `keep_offline_only` |

---

## 4. Governing Rules For This Ladder

1. `incident packet` remains canonical decision unit.
2. Temporal 线不得替代当前两段主运行面；它只能增强：
   - trigger policy
   - calibration threshold
   - teacher routing
   - human gate
   - shadow action compare
3. 所有 successor family 必须继续满足：
   - `anti_leakage_violation_count = 0`
   - 不把 `coarse_text_time` / `unknown_time` 当 admission-grade evidence
4. 任何 temporal family 都不得拿来声称：
   - `DV2` 已经通过
   - schema day-span 已经满足
   - local small model 已经重新 admissible
5. successor ladder 是 **conditional**；前一阶 proof bar 不满足，则 ladder 在该处停止。

---

## 5. Successor Ladder P7 -> P10

| Family | Core question | Expected output class | To next family only if |
|---|---|---|---|
| `P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT` | temporal delta 什么时候值得影响 trigger / threshold？ | policy compare + threshold audit artifacts | 存在 bounded、non-empty、anti-leakage policy delta |
| `P8_QUEUE_ROUTING_UTILITY_AND_BUDGET_COMPARE` | temporal-aware trigger 是否提升 teacher / human queue utility？ | queue utility + budget compare artifacts | queue utility 不退化且 budget 仍受控 |
| `P9_SHADOW_ACTION_POLICY_INTEGRATION_COMPARE` | temporal-aware policy 是否值得影响 shadow action decision？ | shadow action compare artifacts | action-level utility 存在且 major metrics 不退化 |
| `P10_RUNTIME_ADMISSION_AND_GUARDRAILS` | temporal overlay 是否可以 bounded 准入 runtime？ | config / guardrail / rollback / admission artifacts | overlay 有明确 admission verdict |

---

## 6. P7 — `TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT`

## 6.1 Mission

P7 只回答一个问题：

> 当前 P6 证明存在的 selective hybrid / temporal score delta，什么时候值得影响 trigger policy 与 calibration threshold？

P7 不应继续做新的 retrieval family 变体；它应开始把 temporal 信号翻译为 **可进入决策面的候选 policy band**。

## 6.2 In scope

- trigger-policy compare under anti-leakage discipline
- calibration-threshold audit
- score-delta usefulness audit beyond retrieval-only surface
- raw vs selective vs temporal-aware trigger compare
- bounded packet-level / fold-level policy delta artifact

## 6.3 Out of scope

- queue utility compare
- shadow action policy integration
- runtime admission
- new temporal model / new embedding family / new sidecar

## 6.4 Suggested output artifacts

- `data/eval/temporal-trigger-policy-audit.json`
- `data/eval/temporal-trigger-policy-audit.md`
- `data/eval/temporal-calibration-threshold-audit.json`
- `data/eval/temporal-calibration-threshold-audit.md`

## 6.5 Proof bar

P7 只有同时满足下列条件，才允许创建 P8：

1. `anti_leakage_violation_count = 0`
2. 至少存在一个 bounded temporal policy band，使得：
   - `packets_with_policy_delta_gt_raw > 0`
   - `folds_with_policy_delta > 0`
3. major packet / episode metrics 相对 raw baseline 不退化
4. policy delta 不是靠“把几乎所有 packet 都送进 temporal lane”得到的
5. artifact 能说明 budget delta，而不是只报告 retrieval delta

## 6.6 Stop condition

满足任一项则停止 ladder：

1. temporal 只能改变 retrieval score，不能形成非空 policy delta
2. temporal policy delta 只能通过接近 always-on 的宽路由得到
3. temporal trigger 会引入 leakage 或 major metric regression
4. temporal 信号与现有 `novelty / confidence / blast_radius` trigger 几乎完全重合，没有新增决策价值

---

## 7. P8 — `TEMPORAL_ALIGNMENT_P8_QUEUE_ROUTING_UTILITY_AND_BUDGET_COMPARE`

## 7.1 Mission

P8 只在 P7 证明存在可信 policy band 后才成立。

它回答的问题是：

> temporal-aware trigger 是否真的改善 teacher / human queue utility，而不是只制造更多队列流量？

## 7.2 In scope

- teacher queue utility compare
- human gate utility compare
- budget-aware compare
- high-risk / hard-case concentration compare
- queue delta attribution to temporal signal

## 7.3 Out of scope

- shadow action policy integration
- runtime admission
- production queue rollout

## 7.4 Suggested output artifacts

- `data/eval/temporal-queue-routing-utility.json`
- `data/eval/temporal-queue-routing-utility.md`

## 7.5 Proof bar

P8 只有同时满足下列条件，才允许创建 P9：

1. temporal-aware queue 的 utility 不低于 raw queue
2. queue utility 增益不是通过无界增大 queue size 获得
3. `budget_regression = false`
4. temporal-aware queue 至少在一个有意义子集上提升：
   - hard-case concentration
   - severe / page-worthy concentration
   - teacher / human 审核价值
5. packet severe recall / top-K precision / episode precision 不退化

## 7.6 Stop condition

满足任一项则停止 ladder：

1. queue 变大但 utility 不提升
2. queue utility 轻微提升但 budget 明显恶化
3. temporal signal 只是在重复现有 trigger，而没有额外区分力
4. temporal queue compare 无法产生稳定的 hard-case concentration 改善

---

## 8. P9 — `TEMPORAL_ALIGNMENT_P9_SHADOW_ACTION_POLICY_INTEGRATION_COMPARE`

## 8.1 Mission

P9 只在 P8 证明 temporal-aware queue utility 存在后才成立。

它回答的问题是：

> temporal-aware policy 是否值得影响当前 shadow decision surface，而不仅仅影响 teacher / human queue？

## 8.2 In scope

- raw shadow action policy vs temporal-aware shadow action policy compare
- bounded action delta audit
- action reason-code / attribution audit
- shadow-only integration compare

## 8.3 Out of scope

- runtime admission
- production action enablement
- replacing current score thresholds wholesale

## 8.4 Suggested output artifacts

- `data/eval/temporal-shadow-action-policy-compare.json`
- `data/eval/temporal-shadow-action-policy-compare.md`

## 8.5 Proof bar

P9 只有同时满足下列条件，才允许创建 P10：

1. `action_policy_delta_count > 0`
2. action delta 只作用于 bounded subset，而不是全面改写 shadow decisions
3. action delta 可以被解释为 temporal policy result，而不是偶然 artifact noise
4. major packet / episode metrics 不退化
5. teacher / human queue 没有因 action integration 而失控膨胀

## 8.6 Stop condition

满足任一项则停止 ladder：

1. action delta 不存在或只在极小偶然样本上存在
2. action delta 存在但无法解释或无法审计
3. action delta 会明显恶化 human gate / escalation pressure
4. 复杂度进入 shadow decision surface，但没有动作层收益

---

## 9. P10 — `TEMPORAL_ALIGNMENT_P10_RUNTIME_ADMISSION_AND_GUARDRAILS`

## 9.1 Mission

P10 只在 P9 证明 temporal-aware action utility 存在后才成立。

它回答的问题是：

> temporal overlay 是否已经具备 bounded shadow/runtime admission 所需的 config、guardrail、rollback 与 verdict surface？

## 9.2 In scope

- config surface definition
- feature-flag / kill-switch shape
- guardrail bars
- rollback criteria
- shadow runtime admission verdict

## 9.3 Out of scope

- production full rollout
- local small model rerun admission
- schema-gate override
- temporal sidecar productionization

## 9.4 Suggested output artifacts

- `data/eval/temporal-runtime-admission.json`
- `data/eval/temporal-runtime-admission.md`
- optional config additions under `configs/`
- optional shadow/runtime flag integration under current pipeline scripts

## 9.5 Proof bar

P10 只有在满足下列条件时，temporal 线才算接近终点：

1. temporal overlay 有显式 config surface，而不是散落在代码里的隐式逻辑
2. temporal overlay 有 kill-switch / rollback path
3. temporal overlay 仍保持 packet-centric、bounded、anti-leakage
4. closeout verdict 明确为以下二选一之一：
   - `admit_to_shadow_runtime`
   - `keep_offline_only`

## 9.6 Stop condition

满足任一项则 ladder 在 P10 结束并收束为 offline-only：

1. 无法定义稳定 config / threshold / guardrail surface
2. temporal overlay 依赖脆弱手调，缺少 rollback 规则
3. admission 价值只停留在分析面，不能形成 shadow/runtime-ready surface

---

## 10. What Counts As “Merged Into Main Runtime”

当前阶段，“并入主 runtime”不等于 production full rollout。

Temporal 线被视为已并入主 runtime，至少要满足：

1. temporal overlay 先以 `shadow runtime` 身份存在
2. temporal overlay 只影响 bounded decision surface：
   - teacher trigger
   - human gate
   - shadow action compare
3. temporal overlay 有显式 config + guardrail + rollback
4. temporal overlay 不改变 canonical unit、不绕开 schema gate、不提前推动 local-small-model admission
5. current hardening / shadow pipeline 可以在 **flag-on / flag-off** 两种模式下运行并做 compare

换句话说，temporal 线真正并入主 runtime 的最小定义是：

> `runtime integration = shadow-first, bounded, reversible, packet-centric temporal decision overlay`

---

## 11. What Counts As “Collapse / Closure”

满足以下任一条件，应视 temporal successor ladder 收束，而不是继续扩写新 family：

1. P7 无法证明 temporal score delta 能形成 bounded policy delta
2. P8 无法证明 temporal-aware queue utility
3. P9 无法证明 temporal-aware action utility
4. P10 无法形成 config / guardrail / rollback surface
5. temporal 长期只能输出“score looks better”，却无法进入决策面

收束后的正确结论应是：

- temporal line remains valuable as:
  - eval discipline
  - anti-leakage truth
  - retrieval audit surface
- temporal line is **not admitted** as runtime decision overlay
- no further successor family should be created unless new evidence surface appears

---

## 12. Relationship To Other Workstreams

## 12.1 Relationship to blocked `DV2`

该 ladder 与：

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL`
- `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT`

保持正交。

Temporal ladder：

- 不等待 next date 才能继续做 offline compare
- 但绝不能被拿来伪造 schema gate progress

## 12.2 Relationship to current two-stage runtime

Temporal ladder 的存在是为了增强当前：

```text
incident packet -> retrieval -> cheap student -> teacher -> human
```

不是为了替换它。

## 12.3 Relationship to local small model

Temporal ladder 的成功也**不自动**等于：

- local small model rerun admission
- local student implementation admission

它只能说明：

- temporal signal 是否值得进入当前 runtime 的 bounded decision surface

---

## 13. Authoring Rule Before Creating P7 Pack

在创建 `TEMPORAL_ALIGNMENT_P7_*` plan/status/workset 之前，应先接受本 ladder 作为 governing memo。

P7 pack 必须：

1. 明确引用本文件
2. 明确只服务于 `P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT`
3. 不预先承诺 P8-P10 一定执行
4. 只在 P7 closeout 证明 proof bar 满足后，才创建 P8 pack

---

## 14. Next Action

本 memo 落地后，下一步不是直接写 P8/P9/P10，而是：

1. 创建并激活 `TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT` pack
2. 在 P7 内仅围绕：
   - trigger-policy compare
   - calibration-threshold audit
   - score-delta usefulness audit
3. 用 P7 closeout 来决定：
   - `continue_to_P8`
   - or `collapse_temporal_ladder_here`
