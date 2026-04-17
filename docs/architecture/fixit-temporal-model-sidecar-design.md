# fixit temporal model sidecar design

- Status: `proposed-sidecar-ssot`
- Scope: `temporal lane / time-series foundation model sidecar / packet enrichment / ranking / teacher gating / Granite-Gemma cooperation`
- Repo: `/home/peng/dt-git/github/fixit`
- Last updated: `2026-04-17`
- Primary reader: 后续负责把 `TimesFM / Chronos family` 这类时间序列模型接入 `fixit` 的执行者

---

## 1. Decision Summary

### 1.1 Chosen architectural framing

`fixit` 若引入 `TimesFM / Chronos / Chronos-2` 这类时间序列 foundation model，正确角色应冻结为：

- **`temporal sidecar`，不是新的 final judge**
- `incident packet` 继续保持 canonical decision unit
- 时间序列模型的输入应是 **bounded telemetry 派生出的 multi-channel temporal panel**，不是 raw log body 直喂
- 时间序列模型的输出应是：
  - `temporal anomaly`
  - `persistence risk`
  - `self-heal probability`
  - `incident phase`
  - `future escalation risk`
  - `temporal signature`
- 上述输出应写回 packet 的 `temporal` section，并被下游用于：
  - candidate generation
  - queue ranking
  - teacher gating
  - student feature enrichment
- 当前 repo 已冻结的主运行面 **不因此改变**：
  - `cheap dense scorer -> teacher -> human gate`
- 当前已冻结的 `Granite 2B` 实现路线 **不因此被替代**：
  - temporal lane 只作为 sidecar enrich 它

### 1.2 What changes if this lane is added

系统能力会从主要回答：

- “这个窗口现在像不像事故？”

升级为也能回答：

- “它是在恶化、扩散、平台期还是恢复？”
- “它是 transient spike，还是持续性故障？”
- “当前看起来还不算最严重，但未来 `10-30` 分钟是否很可能升级？”
- “它是否更值得消耗 teacher budget / human attention？”

### 1.3 Explicit non-goals

引入 temporal lane 后，仍然**不**做下列事：

- 不把 raw logs 直接当时间序列模型的主要输入对象
- 不让时间序列模型直接输出最终 `page_owner` / `escalate` 决策
- 不让时间序列模型替代 `Granite 2B student`
- 不让时间序列模型替代 `Gemma4 teacher`
- 不让时间序列模型绕过 `human gate`
- 不把 canonical unit 从 `incident packet` 改回原始日志流

---

## 2. Why a temporal lane is worth adding

## 2.1 Current system is strong on snapshot triage, weaker on temporal dynamics

当前 `fixit` 已经较强的面：

- bounded telemetry -> candidate window -> `incident packet`
- rules + retrieval + structured student
- `Gemma4 teacher` 处理高价值 hard case
- `human outcome` / `production outcome` 作为高优先级标签

当前相对偏弱的面：

- 区分 `transient burst` vs `sustained failure`
- 区分 `onset` vs `recovery`
- 识别 `future worsening risk`
- 按“动态形态”做 retrieval / teacher routing
- 对“当前不高，但很快会升级”的 case 做更早判定

## 2.2 Logs do contain temporal signal, but not in raw-line form

日志具备天然时间属性，但其可建模单位不应是原始文本流本身，而应是：

- template counts over time
- template entropy / churn over time
- retry / timeout / db-error families over time
- unique exception counts over time
- log error density over time
- 与 metrics / traces 对齐后的 multi-signal panel

也就是说，真正应该建模的是：

- **log-derived temporal channels**

而不是：

- **unbounded raw log lines**

## 2.3 New opportunity surface opened by temporal modeling

| Opportunity | Current weakness | Temporal lane gain |
|---|---|---|
| Early warning | 主要看当前窗口严重性 | 提前看到 worsening / precursor |
| Transient suppression | 静态 snapshot 易把尖峰当事故 | 区分 burst vs sustained |
| Ranking by future risk | 现在更像按当前风险排序 | 可按 future escalation risk 排序 |
| Teacher budget routing | 主要靠 novelty / confidence | 增加 persistence / phase / forecast disagreement |
| Human review usability | 以静态 summary 为主 | 加入 `onset/spread/recovery` 阶段信息 |
| Similar incident retrieval | 主要靠语义与历史标签 | 增加 temporal signature 相似检索 |

---

## 3. Correct role of `TimesFM / Chronos family` inside `fixit`

## 3.1 Freeze the role, not the backend winner

架构层当前应冻结的是：

- `temporal sidecar contract`

而不是立刻冻结：

- “必须是 `TimesFM`”
- 或“必须是 `Chronos-2`”

更稳妥的做法是：

- 把 `TimesFM`、`Chronos / Chronos-2 family` 都看成 **候选 temporal backend**
- 在相同 `panel -> temporal_output` contract 下做 shadow compare
- 由 replay / ablation / system metrics 决定哪个 backend 更值得保留

## 3.2 Proper jobs for time-series foundation models

在 `fixit` 中，这类模型更适合承担：

1. `forecast residual` 计算
2. `persistence risk` 估计
3. `self-heal probability` 估计
4. `change-point / phase` 摘要
5. `future escalation risk` 先验
6. `temporal signature embedding`（后续增强）

## 3.3 Jobs they should not own

不应让它们承担：

1. 原始日志语义理解主任务
2. 最终 action recommendation 主判定
3. 跨服务复杂根因 prose 解释
4. 全量替代 `Granite 2B` 的 packet-level structured triage
5. 全量替代 `Gemma4 teacher` 的 hard-case judgment

## 3.4 Architecture consequence

因此 `TimesFM / Chronos family` 的正确定位是：

- `temporal prior engine`

而不是：

- `semantic incident judge`

---

## 4. End-to-end placement in the current architecture

## 4.1 Recommended placement

```text
bounded raw telemetry
  -> candidate windows
  -> template aggregation / bucketization / multi-signal temporal panels
  -> temporal sidecar (TimesFM / Chronos family)
  -> packet.temporal enrichment
  -> current structured baseline / Granite 2B student
  -> Gemma4 teacher on selected hard cases
  -> human gate
  -> outcomes / labels / temporal evaluation artifacts
```

## 4.2 What remains unchanged

以下真相不变：

- `incident packet` remains canonical
- current runtime default remains `cheap dense scorer -> teacher -> human`
- `Granite 2B` remains the current small-student implementation track
- `Gemma4 26B` remains remote teacher / distillation source

## 4.3 What newly becomes possible

temporal lane 加入后，系统可新增两个插点：

### A. Before packet finalization

用于：

- 候选窗口过滤 / 补充
- 早期 anomaly prior
- 未来风险初筛

### B. After packet finalization

用于：

- `packet.temporal` enrichment
- student 特征扩展
- teacher routing
- queue ranking

---

## 5. Data-plane design

## 5.1 Governing rule

时间序列侧车的数据面必须满足：

- bounded
- reproducible
- cutoff-aware
- no future leakage
- aligned to packet window

## 5.2 Prediction cutoff contract

每个 temporal prediction 必须带清楚：

- `cutoff_at`
- `lookback_minutes`
- `bucket_seconds`
- `horizon_minutes`

规则：

- temporal lane 只能使用 `cutoff_at` 之前的信号
- 不允许用 packet 之后的窗口信息回填当前预测
- 所有 shadow / calibration / offline compare 必须按同一 cutoff 回放

## 5.3 Source -> target mapping

| Source | Derived target | Use |
|---|---|---|
| `data/samples/raw/log_evidence.jsonl` | `log-template panel` | log temporal channels |
| `data/samples/raw/metrics_windows.jsonl` | `metric panel` | metrics temporal channels |
| `data/samples/raw/trace_evidence.jsonl` | `trace panel` | trace temporal channels |
| `data/samples/raw/topology.jsonl` + control-plane context | `correlation context` | upstream/downstream agreement |
| candidate window metadata | `panel cutoff / horizon metadata` | no-leak replay |
| historical incidents / outcomes | `temporal archetype labels` | later retrieval / eval |

## 5.4 Recommended temporal channels

### A. Logs-derived channels

优先从日志派生：

- `error_count_t`
- `warn_count_t`
- `fatal_count_t`
- `unique_template_count_t`
- `template_entropy_t`
- `template_churn_rate_t`
- `novel_template_ratio_t`
- `retry_template_rate_t`
- `timeout_template_rate_t`
- `db_error_template_rate_t`
- `auth_error_template_rate_t`
- `distinct_exception_count_t`
- `log_error_density_t`

### B. Metrics-derived channels

优先从 metrics 派生：

- `error_rate_t`
- `p95_latency_t`
- `p99_latency_t`
- `qps_t`
- `cpu_util_t`
- `memory_pressure_t`
- `saturation_proxy_t`

### C. Traces-derived channels

优先从 traces 派生：

- `trace_error_ratio_t`
- `top_operation_latency_t`
- `failed_span_count_t`
- `upstream_timeout_ratio_t`
- `dependency_error_ratio_t`

### D. Topology / routing-derived channels

优先从 topology / routing 派生：

- `upstream_correlated_anomaly_count_t`
- `downstream_correlated_anomaly_count_t`
- `blast_radius_proxy_t`
- `deploy_marker_t`

## 5.5 Recommended bucket policy

建议第一版统一使用：

- short panel: `60s` bucket, `60m` lookback
- coarse panel: `300s` bucket, `6h` lookback

原因：

- `60s` panel 更利于 onset / burst / short spike
- `300s` panel 更利于 persistence / trend / slow degradation
- 双 panel 方案更适合 logs 与 metrics 的混合节奏

## 5.6 Recommended artifacts

建议新增但不强制立即落地的产物路径：

- `data/samples/temporal/log-template-panels.jsonl`
- `data/samples/temporal/metric-panels.jsonl`
- `data/samples/temporal/trace-panels.jsonl`
- `data/samples/temporal/fused-panels.jsonl`
- `data/eval/temporal/sidecar-predictions.jsonl`
- `data/eval/temporal/sidecar-shadow-compare.json`
- `data/eval/temporal/sidecar-ablation.json`
- `data/eval/temporal/temporal-feature-ledger.json`

## 5.7 Minimal fused panel row shape

```json
{
  "panel_id": "tp_g-crm-campaign_2026-04-17T10:35:00Z",
  "service": "g-crm-campaign",
  "env": "prod",
  "packet_id": "ipk_0042",
  "cutoff_at": "2026-04-17T10:35:00Z",
  "lookback_minutes": 60,
  "bucket_seconds": 60,
  "horizon_minutes": 15,
  "channels": {
    "error_count": [0, 0, 1, 3, 8, 13],
    "template_entropy": [0.1, 0.1, 0.2, 0.5, 0.8, 0.9],
    "retry_template_rate": [0.0, 0.0, 0.1, 0.3, 0.6, 0.7],
    "trace_error_ratio": [0.01, 0.02, 0.02, 0.10, 0.24, 0.41],
    "p95_latency": [120, 130, 128, 180, 260, 410]
  }
}
```

---

## 6. Packet schema extension

## 6.1 Governing rule

不改变 `incident packet` 的 canonical 地位；只新增一个 bounded `temporal` section。

## 6.2 Recommended `packet.temporal` shape

```json
{
  "temporal": {
    "cutoff_at": "2026-04-17T10:35:00Z",
    "lookback_minutes": 60,
    "bucket_seconds": 60,
    "horizon_minutes": 15,
    "model_family": "timesfm|chronos|chronos2|none",
    "model_version": "...",
    "temporal_anomaly_score": 0.84,
    "forecast_residual_score": 0.79,
    "persistence_risk": 0.72,
    "self_heal_probability": 0.18,
    "worsening_velocity": 0.67,
    "future_escalation_risk": 0.70,
    "incident_phase": "onset",
    "time_to_threshold_minutes": 12,
    "cross_signal_agreement": 0.81,
    "temporal_signature_id": "sig_retry_timeout_ramp_v1",
    "top_temporal_reasons": [
      "retry_rate_accelerating",
      "trace_error_ratio_rising",
      "template_entropy_break"
    ]
  }
}
```

## 6.3 Field semantics

| Field | Meaning | Primary consumer |
|---|---|---|
| `temporal_anomaly_score` | 当前动态形态偏离历史/近期 baseline 的强度 | candidate generation / ranking |
| `forecast_residual_score` | 预测残差强度 | anomaly prior |
| `persistence_risk` | 问题持续而非短暂抖动的概率 | teacher gating / suppress false page |
| `self_heal_probability` | 问题自动回落概率 | ranking / human gate |
| `worsening_velocity` | 恶化速度 | priority queue |
| `future_escalation_risk` | 未来短时窗升级风险 | early warning / teacher routing |
| `incident_phase` | `onset|spread|plateau|recovery|unknown` | human review usability |
| `cross_signal_agreement` | logs / metrics / traces 是否共振 | teacher gating |
| `temporal_signature_id` | 动态模式签名 | later retrieval / clustering |
| `top_temporal_reasons` | 可读的 sidecar reason codes | Granite / Gemma prompt context |

## 6.4 Rendered packet addition for `Granite 2B`

建议在 packet render 中新增：

```text
[temporal]
incident_phase=onset
temporal_anomaly_score=0.84
persistence_risk=0.72
self_heal_probability=0.18
future_escalation_risk=0.70
cross_signal_agreement=0.81
temporal_signature_id=sig_retry_timeout_ramp_v1
reason_1=retry_rate_accelerating
reason_2=trace_error_ratio_rising
reason_3=template_entropy_break
```

这样 temporal lane 的输出可直接进入 `Granite 2B` 的 structured triage 输入，而不要求 Granite 直接看原始时间序列数组。

---

## 7. New opportunities unlocked for the whole system

## 7.1 Early-warning ranking

系统可从“当前严重性排序”升级到“未来风险排序”：

- 当前不高但 `future_escalation_risk` 高的 packet 提前上浮
- 当前 noisy 但 `self_heal_probability` 高的 packet 下沉

## 7.2 Better transient-noise suppression

系统可更好地区分：

- deploy spike
- retry burst
- one-off timeout storm
- sustained failure
- recovery tail

价值：

- 降误报
- 降 teacher burden
- 降 human 无效 page
- 少堆 suppress heuristics

## 7.3 Phase-aware human review

human gate 将获得更可操作的动态信息：

- `onset`
- `spread`
- `plateau`
- `recovery`

这样人工判断不再只依赖静态 summary。

## 7.4 Temporal retrieval and archetypes

后续可扩展：

- 按 `temporal_signature_id` 检索相似事故
- 按动态形态而不是文本模板做 incident clustering
- 找到“语义不同但演化形态相似”的历史 severe incident

## 7.5 Better teacher routing

teacher budget 可不再只依赖：

- low confidence
- high novelty
- high blast radius

还可加入：

- `future_escalation_risk` 高
- `persistence_risk` 高
- `Granite` 与 temporal lane 强冲突
- 当前看似普通但 temporal signature 像历史 severe precursor

---

## 8. Cooperation with current baseline, `Granite 2B`, and `Gemma4 teacher`

## 8.1 Current structured baseline control arm

当前 baseline control arm 仍应保留，并优先尝试先吃 temporal 数值特征：

- `temporal_anomaly_score`
- `persistence_risk`
- `self_heal_probability`
- `future_escalation_risk`
- `incident_phase`（one-hot / ordinal）
- `cross_signal_agreement`

原因：

- 先验证 temporal lane 的真实增益是否存在
- 先用低复杂度控制组做 ablation
- 避免一开始把所有增益都误归因给 `Granite 2B`

## 8.2 `Granite 2B student`

`Granite 2B` 的正确接法不是直接吞时间序列数组，而是：

- 吃带 `temporal` section 的 rendered packet
- 把 temporal priors 当成额外 structured evidence
- 仍输出：
  - `severity_band`
  - `needs_teacher`
  - `recommended_action`
  - `reason_codes`
  - `confidence_band`

### Expected benefits for Granite

temporal lane 可帮助 Granite 更好处理：

- `snapshot 看起来不高，但未来风险高`
- `日志语义普通，但动态形态危险`
- `短时 burst 不值得升级`
- `进入 recovery phase 的误报压降`

## 8.3 `Gemma4 teacher`

`Gemma4 teacher` 应接收压缩后的 temporal summary，而不是完整时序数组。

建议 teacher request 增加：

- `incident_phase`
- `future_escalation_risk`
- `persistence_risk`
- `self_heal_probability`
- `cross_signal_agreement`
- `Granite-vs-temporal disagreement flags`

### Expected benefits for teacher

teacher 可更快理解：

- 当前 case 是“动态高风险”还是“语义高风险”
- 是否需要 override Granite
- 是否需要优先升级给 human

## 8.4 Disagreement rules worth escalating

以下冲突值得直接提高 teacher 优先级：

1. `Granite low risk` + `future_escalation_risk high`
2. `Granite says observe` + `persistence_risk high`
3. `Granite high risk` + `self_heal_probability high`
4. control arm 与 Granite 一致低风险，但 temporal signature 高度近似历史 severe incident
5. `incident_phase = onset` 且 `worsening_velocity` 很高，但规则尚未命中

---

## 9. Evaluation framework

## 9.1 Governing rule

评估 temporal lane 不能只看 forecast accuracy；必须看 **对 triage system 的增益**。

因此评估分三层：

1. temporal-model local metrics
2. packet / ranking / gating metrics
3. whole-system shadow metrics

## 9.2 Layer 1 — temporal-model local metrics

可选但不应成为唯一决策依据：

- `MAE / RMSE / sMAPE` on selected channels
- change-point detection hit rate
- persistence classification AUC
- phase classification accuracy

说明：

- 这些指标只证明 temporal backend 有局部能力
- 不足以证明它值得进入 `fixit` runtime

## 9.3 Layer 2 — packet / gating metrics

真正更重要的中间层指标：

- `transient suppression precision`
- `persistent failure recall`
- `early_warning_lead_time_p50/p90`
- `teacher queue lift`（同 budget 下 teacher 看到了更多高价值 case）
- `future severe precursor recall`
- `Granite-temporal disagreement precision`
- `packet.temporal coverage rate`

## 9.4 Layer 3 — whole-system shadow metrics

最终仍要回到 `fixit` 主指标：

- severe recall
- top-K precision
- teacher escalation rate
- fallback burden
- missed severe count
- action confusion matrix
- human-review usefulness rate

### Protection rule

temporal lane 不允许因为“看起来更聪明”而放宽当前 bars；仍应沿用：

- success recall floor = `1.0`
- success top-K precision floor = `1.0`
- success teacher escalation ceiling = `0.15`
- rollback precision trigger = `0.95`

## 9.5 Temporal-specific ablations

必须做的 ablation：

1. baseline only
2. baseline + engineered temporal features
3. baseline + temporal sidecar outputs
4. Granite only
5. Granite + temporal sidecar
6. Granite + temporal sidecar + teacher

问题必须能回答：

- temporal lane 的增益是否真实存在？
- 这个增益是来自 engineered features，还是来自 TS foundation model？
- temporal lane 是否只是把已有 metrics feature 重复编码了一遍？

## 9.6 Leakage and honesty checks

必须新增 honest-check：

- prediction cutoff audit
- no-future-window audit
- same-window alignment audit
- service-holdout / date-holdout compare

若 leakage audit 不过，则整个 temporal result 无效。

---

## 10. Rollout order

## 10.1 Recommended adoption ladder

### T0 — engineered temporal features only

先不引入 TS foundation model，只做：

- slope
- acceleration
- burstiness
- entropy break
- change-point heuristics

目的：

- 建立控制组
- 验证 temporal information 本身是否有价值

### T1 — temporal sidecar backend shadow

在相同 panel contract 下，离线比较：

- `TimesFM`
- `Chronos / Chronos-2`

目的：

- 比较 forecast residual / persistence / phase summary 的实用性
- 不急于冻结 backend winner

### T2 — packet enrichment only

先让 temporal outputs 只写回 `packet.temporal`，不直接改 runtime gating。

### T3 — teacher gating / ranking

若 shadow 证明有增益，再进入：

- teacher routing
- queue ordering
- early-warning ranking

### T4 — Granite integration

若前面通过，再把 `packet.temporal` 稳定加入 Granite 训练 / 推理输入。

## 10.2 Why this order matters

这样可以避免：

- 一开始就把 temporal backend、Granite、teacher routing 全绑死
- 无法判断增益来源
- 出现问题时没有低复杂度回滚面

---

## 11. Risks and boundary rules

## 11.1 Main risks

### Risk A — leakage

未来信息泄漏到当前预测，会让 temporal lane 看起来“神准”，但系统上不可用。

### Risk B — sparse and irregular logs

日志不像 metrics 那样天然规则采样；不同服务可能极其稀疏，必须先 bucketize / aggregate。

### Risk C — service-specific drift

不同服务的日志模板、节奏、deploy pattern 差异很大；不能假设全局一个 temporal backend 自然泛化。

### Risk D — duplicated truth

若 temporal lane 自己又维护一套 severity 语义，容易和 rules / retrieval / Granite / teacher 再次分裂。

## 11.2 Boundary rules

必须坚持：

- temporal lane 只输出 `temporal priors`，不输出最终 gold severity truth
- temporal lane 的结果必须写回 packet，而不是形成独立平行决策宇宙
- temporal lane 进入 runtime 前必须先完成 ablation + leakage audit + shadow compare
- `Gemma4 teacher` 与 `Granite 2B` 的角色不因 temporal lane 而被重写

---

## 12. Final recommendation

`fixit` 若加入 `TimesFM / Chronos family` 这类时间序列模型，最正确的系统设计不是：

- `raw logs -> time-series model -> final decision`

而是：

- `bounded telemetry -> temporal panels -> temporal sidecar -> packet.temporal enrichment -> baseline / Granite 2B -> Gemma4 teacher -> human gate`

冻结的关键结论是：

1. temporal lane 是 **sidecar**，不是新总判官
2. `incident packet` 继续是 canonical decision unit
3. `TimesFM` 与 `Chronos family` 当前只冻结为 **候选 backend**，不先冻结单一赢家
4. temporal lane 的核心价值在：
   - early warning
   - transient suppression
   - persistence / self-heal judgement
   - teacher routing
   - future-risk ranking
5. temporal lane 与 `Granite 2B`、`Gemma4 teacher` 是互补关系，不是替代关系

一句话总结：

> `fixit` 的下一步不是让时间序列模型取代语义 triage，而是让它成为一条 bounded、可评测、可回滚的 temporal prior lane，把系统从“静态快照判定”升级到“语义 × 时间 × 拓扑”的 incident intelligence。
