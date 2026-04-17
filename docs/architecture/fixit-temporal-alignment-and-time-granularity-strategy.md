# fixit temporal alignment and time granularity strategy

- Status: `proposed-temporal-alignment-ssot`
- Scope: `temporal lineage / timestamp quality / effective time granularity / episode-aware split / time-aware eval / current historical-data exploitation`
- Repo: `/home/peng/dt-git/github/fixit`
- Last updated: `2026-04-17`
- Primary reader: 后续负责把历史数据时间对位、offline 训练评测、temporal sidecar 数据面对齐到同一 contract 的执行者

---

## 1. Decision Summary

### 1.1 Chosen strategy

当前 `fixit` 的正确 temporal strategy 冻结为：

- `incident packet` 继续保持 canonical decision unit
- 当前优先做 **temporal alignment**，而不是优先引入长时序模型
- 时间应首先被视为：
  - lineage attribute
  - eval / split / cutoff discipline
  - retrieval recency / teacher routing / persistence 判断的支持面
- 当前 repo 的历史数据虽然没有多周/多月严格 machine-timestamped training set，但已经具备足够的 **时间锚点 + 可继承时间关系**，可以建立有效时间对应性
- 当前应采用 **timestamp_quality 分层**，而不是把所有历史样本强行当成同质量时序样本
- 当前最有效的时间粒度不是“长序列模型输入粒度”，而是：
  - `5m window`
  - `15-60m episode`
  - `day-level operational stability`

### 1.2 Consequence

对当前任务目标：

- **时间不是强 long-sequence modeling dependency**
- **时间是强 alignment / leakage-control / admission-evidence dependency**

因此当前应优先建设：

1. temporal lineage
2. timestamp quality taxonomy
3. packet-linked derived timestamps
4. episode-aware split
5. time-aware offline eval

而不是优先建设：

- RNN / LSTM / Transformer over long packet streams
- 周/月级 forecasting-first runtime
- 用文本月级 hint 冒充精确时序训练集

### 1.3 Explicit non-goals

当前策略明确不做：

- 不把 `coarse text time` 当成 `exact timestamp`
- 不用 same-day schema snapshots 冒充 multi-day stability
- 不因历史离线训练可运行，就跳过 `DV2` 的真实 next-date gate
- 不让 temporal lane 替代 `packet -> student -> teacher -> human` 主运行面

---

## 2. Current Repo Truth

## 2.1 What already has exact machine time

当前 repo 内最强时间锚点来自：

- `data/samples/raw/metrics_windows.jsonl`
- `data/samples/fixtures/metrics_windows.retained.jsonl`
- `data/samples/replay/metrics_windows.jsonl`
- `data/samples/candidate-windows.jsonl`
- `data/samples/incident-packets.jsonl`

其中：

- `metrics_windows` 有明确 `ts_start` / `ts_end`
- `candidate windows` 继承该时间窗
- `incident packets` 直接把 `ts_start` / `ts_end` 写入 packet schema

当前可确认的强时间范围：

- earliest exact machine time: `2026-04-16T11:25:00Z`
- latest exact machine time: `2026-04-16T12:25:00Z`

这意味着：

- 当前 repo 已具备 **精确窗口级时间对位能力**
- 只是该能力目前主要集中在 packet 生产面，而不是均匀存在于所有 supervision 文件中

## 2.2 What can inherit exact time through lineage

以下文件虽无显式时间戳，但可通过 lineage 继承 packet 时间：

- `data/eval/outcomes.jsonl` via `packet_id`
- `data/eval/manual_teacher_judgements.jsonl` via `packet_id`
- `data/eval/training_examples.jsonl` 中的 packet-linked rows via `packet_id`
- `data/eval/historical_incidents.jsonl` via `source_packet_id` / `source_packet_ids`

当前已验证的 repo truth：

- `outcomes`: `10/10` packet-linked
- `manual_teacher_judgements`: `10/10` packet-linked
- `training_examples`: `16` total，其中 `10` 条 packet-linked，`6` 条 legacy unlinked
- `historical_incidents`: `4` incidents，合计 `10` 个 `source_packet` 引用，可映射到 packet 时间

结论：

- 当前监督数据并不是“完全无时间”
- 当前监督数据是“**部分显式时间 + 大量可继承时间**”

## 2.3 What only has coarse time hints

当前 `memory_summaries` 只提供粗粒度时间提示，例如：

- `2026-02`
- `2026-03`
- `2026-04`

其价值是：

- retrieval recency hint
- operator memory background
- incident archetype freshness prior

其限制是：

- 不能当 `exact window time`
- 不能用于 strict time-based split
- 不能直接作为 schema/day-span evidence

## 2.4 What is still weak / missing

当前最弱的面不是“完全没有时间概念”，而是：

- supervision 文件缺少统一的派生时间字段
- legacy training rows 仍有 `6` 条无 `packet_id`
- historical incident 当前只有 `source_packet_ids`，缺少显式 `first_seen_ts / last_seen_ts`
- eval 当前仍主要是 packet-level truth，episode-level leak control 尚未显式冻结

---

## 3. Effective Time Granularity

## 3.1 Granularity levels

| Granularity | Current source of truth | Best use | Dependency strength |
|---|---|---|---|
| `5m window` | `metrics_windows`, `candidate-windows`, `incident-packets` | candidate generation / packet scoring / retrieval input | high |
| `15-60m episode` | derived from packet clusters or `historical_incident.source_packet_ids` | split / eval / leakage control / incident grouping | high |
| `day-level` | `schema-stability-history`, accumulation artifacts | schema gate / daily throughput / rerun admission | high |
| `week/month hint` | `memory_summaries`, text summaries | recency prior / operator context | low-to-medium |

## 3.2 Task-by-task temporal dependency

| Task | Temporal dependency | Minimum effective granularity | Notes |
|---|---|---|---|
| candidate generation | medium | `5m window` | already encoded in `metrics_windows` |
| packet severity classification | low-to-medium | `5m window` + a few short-horizon temporal features | not a long-sequence-first task |
| transient vs sustained discrimination | medium-to-high | `15-60m episode` | should not rely on single window alone |
| retrieval ranking | medium | `5m window` + recency prior | avoid future leakage |
| teacher routing | medium | `window` + `episode` | persistence / novelty / future-risk can help |
| schema stability gate | very high | `day-level` | same-day snapshots never count as multi-day evidence |
| small-model rerun admission | high | `day-level` + time-aware eval | must remain honest |

## 3.3 Current recommendation

当前不建议把“时间序列”理解成“必须立刻上时序 backbone”。

当前最有效的 temporal investment 应是：

- `window correctness`
- `episode grouping`
- `time-aware split`
- `cutoff-aware retrieval / eval`
- `day-level admission truth`

---

## 4. `timestamp_quality` Taxonomy

## 4.1 Stable enum

后续 temporal alignment 文档、脚本、artifacts 统一使用以下四档：

### `exact_window_time`

定义：

- 记录本身带显式 `ts_start` / `ts_end` 或等价 machine timestamp

允许用于：

- strict time-based split
- cutoff-aware retrieval
- packet / episode boundary construction
- admission-grade evidence

当前典型文件：

- `metrics_windows*`
- `candidate-windows.jsonl`
- `incident-packets.jsonl`

### `exact_time_inherited`

定义：

- 记录本身无显式时间，但可通过稳定 lineage 映射到 exact packet time

允许用于：

- strict eval
- episode-aware split
- derived incident span
- teacher/outcome/training temporal overlays

当前典型文件：

- `outcomes.jsonl`
- `manual_teacher_judgements.jsonl`
- packet-linked rows in `training_examples.jsonl`
- `historical_incidents.jsonl` via `source_packet_ids`

### `coarse_text_time`

定义：

- 只有文本中月级/粗时间 hint，无精确窗口可继承

允许用于：

- recency prior
- retrieval weighting prior
- operator narrative

禁止用于：

- strict split
- exact eval
- schema/day-span gate

当前典型文件：

- `memory_summaries.jsonl`
- packet `memory.similar_summaries`

### `unknown_time`

定义：

- 没有可靠时间，也无法通过 lineage 继承

允许用于：

- train-only auxiliary supervision
- non-temporal ablation

禁止用于：

- time-aware eval
- cutoff-sensitive retrieval compare
- admission evidence

当前典型文件：

- legacy unlinked rows in `training_examples.jsonl`

## 4.2 Governing rule

训练可以混用多档样本；评估和 admission 不可以。

建议冻结规则：

- train set: `exact_window_time` + `exact_time_inherited` + `unknown_time`（可选）
- eval / validation: 仅使用 `exact_window_time` + `exact_time_inherited`
- admission / gate evidence: 优先 `exact_window_time` + `exact_time_inherited`，绝不接受 `coarse_text_time` / `unknown_time`

---

## 5. Derived Temporal Field Checklist

## 5.1 Governing implementation rule

优先做 **derived temporal overlays / lineage artifacts**，而不是回写篡改原始 retained files。

推荐先新增：

- `data/eval/temporal-lineage.jsonl` — canonical temporal mapping SSOT
- `data/eval/episode-index.json` — episode grouping artifact

必要时再生成 temporalized mirrors，例如：

- `data/eval/replay/outcomes.temporal.jsonl`
- `data/eval/replay/manual_teacher_judgements.temporal.jsonl`
- `data/eval/replay/training_examples.temporal.jsonl`
- `data/eval/replay/historical_incidents.temporal.jsonl`

## 5.2 Canonical derived fields

统一建议字段：

- `derived_ts_start`
- `derived_ts_end`
- `time_granularity`
- `timestamp_quality`
- `time_source`
- `time_source_refs`
- `cutoff_safe` — 是否可用于 cutoff-aware eval
- `episode_id` — P1 引入
- `episode_start_ts` — P1 引入
- `episode_end_ts` — P1 引入

## 5.3 File-by-file checklist

| File | Current anchor | Derived fields to add | Expected quality | Notes |
|---|---|---|---|---|
| `data/samples/replay/metrics_windows.jsonl` | `ts_start`, `ts_end` | `timestamp_quality=exact_window_time`, `time_granularity=window`, `time_source=metrics_window` | `exact_window_time` | already exact; mostly metadata normalization |
| `data/samples/candidate-windows.jsonl` | inherited from metrics window | `timestamp_quality`, `time_granularity`, `time_source=window_id` | `exact_window_time` | keeps candidate lane explicit |
| `data/samples/incident-packets.jsonl` | `ts_start`, `ts_end` | `timestamp_quality`, `time_granularity=window`, later `episode_id` | `exact_window_time` | canonical packet truth |
| `data/eval/outcomes.jsonl` | `packet_id` | `derived_ts_start`, `derived_ts_end`, `timestamp_quality`, `time_source=packet_id` | `exact_time_inherited` | do via overlay / lineage join |
| `data/eval/manual_teacher_judgements.jsonl` | `packet_id` | `derived_ts_start`, `derived_ts_end`, `timestamp_quality`, `time_source=packet_id` | `exact_time_inherited` | keeps teacher supervision time-aware |
| `data/eval/training_examples.jsonl` | packet-linked rows via `packet_id`; others none | packet-linked rows add `derived_ts_*`, `timestamp_quality`; legacy rows mark `timestamp_quality=unknown_time` | mixed | train may keep all rows; eval must filter |
| `data/eval/historical_incidents.jsonl` | `source_packet_ids` | `derived_ts_start=min(source packets)`, `derived_ts_end=max(source packets)`, `time_source=source_packet_ids`, later `episode_id` | `exact_time_inherited` when source refs complete | explicit incident span is needed |
| `data/samples/replay/memory_summaries.jsonl` | text month hints | `derived_time_hint`, `time_granularity=month_hint`, `timestamp_quality=coarse_text_time` | `coarse_text_time` | no strict split use |
| `data/eval/student-scores.jsonl` | `packet_id` | `derived_ts_*`, `timestamp_quality`, later `episode_id` | `exact_time_inherited` | supports time-aware score eval |
| `data/eval/teacher-request-ledger.jsonl` / `teacher-review-ledger.jsonl` / `teacher-fallback-ledger.jsonl` | `packet_id` | `derived_ts_*`, `timestamp_quality`, later `episode_id` | `exact_time_inherited` | allows throughput by episode/day |
| `data/eval/triage-decisions.jsonl` | `packet_id` | `derived_ts_*`, `timestamp_quality`, later `episode_id` | `exact_time_inherited` | needed for time-aware eval |

## 5.4 Recommended `temporal-lineage` record shape

```json
{
  "record_type": "outcome",
  "record_id": "ipk_w001",
  "packet_id": "ipk_w001",
  "derived_ts_start": "2026-04-16T11:25:00Z",
  "derived_ts_end": "2026-04-16T11:30:00Z",
  "time_granularity": "window",
  "timestamp_quality": "exact_time_inherited",
  "time_source": "packet_id",
  "time_source_refs": ["ipk_w001"],
  "cutoff_safe": true
}
```

---

## 6. Episode-aware Split Strategy

## 6.1 Why packet-only split is not enough

若同一 incident episode 的多个 packet 同时出现在 train / eval 两边，会导致：

- retrieval leakage
- label leakage
- optimistic severe recall
- optimistic top-K precision
- teacher routing bias

因此当前应把 split 单位从单 packet 升级到 `episode`。

## 6.2 Episode definition

当前建议使用双层定义：

### Layer A — explicit incident-backed episode

优先使用：

- `historical_incidents.source_packet_ids`

只要一个 incident 明确引用多 packet，就把这一组 packet 视为同一 `episode_id` 的 authoritative source。

### Layer B — heuristic packet cluster

若没有 explicit incident backing，则用启发式聚类：

- same `service`
- same `operation`
- same dominant retrieval incident or same dominant error template family
- time gap within bounded horizon（建议先用 `<= 60m` 作为 soft bound，而不是只按紧邻 5m 连续窗口）

理由：

- 当前同一 incident family 可能跨多个不连续 5m windows
- 只用“连续窗口”会把语义上同一故障错误拆散

## 6.3 Split rules

建议冻结以下规则：

1. 同一 `episode_id` 的所有 packet、training rows、outcomes、teacher judgements 必须落在同一 split。
2. retrieval index 对某个 eval episode 的构建必须满足：
   - 只使用 `derived_ts_end < eval_episode_start_ts` 的历史 incident
   - 不允许把未来 incident summary 放进当前检索库
3. `unknown_time` rows 只允许进入 train，不允许进入 val/test。
4. `coarse_text_time` rows 不进入 strict val/test；如使用，只可作为 retrieval prior，不可作为 gold eval anchor。

## 6.4 Current recommended split mode

鉴于当前 exact-time coverage很窄，当前不推荐立刻做固定 `70/15/15` split。

当前更推荐：

### Option A — leave-one-episode-out

适合当前小样本阶段：

- 每次留一个 episode 做 eval
- 其余 exact/inherited episodes 做 train
- `unknown_time` legacy rows 可只放 train

### Option B — earliest-to-latest rolling cutoff

当未来 exact-time episodes 增多后再采用：

- earlier episodes -> train
- middle episodes -> validation
- latest episodes -> test

## 6.5 Minimal `episode-index` artifact

推荐至少包含：

```json
{
  "episode_id": "ep_compile_500_2026_04_16_a",
  "service": "g-crm-campaign",
  "operation": "ADCService/Compile",
  "packet_ids": ["ipk_w001", "ipk_w004", "ipk_w006", "ipk_w009"],
  "episode_start_ts": "2026-04-16T11:25:00Z",
  "episode_end_ts": "2026-04-16T12:10:00Z",
  "episode_source": "historical_incident_source_packet_ids",
  "timestamp_quality": "exact_time_inherited"
}
```

---

## 7. Experiments That Can Run Now

## 7.1 P0 experiments

### Experiment A — packet-linked historical offline baseline

Goal:

- 仅使用 `exact_window_time` + `exact_time_inherited` 样本验证当前离线链路

Inputs:

- packet-linked `training_examples`
- `outcomes`
- `manual_teacher_judgements`
- `historical_incidents`

Method:

- leave-one-episode-out
- cutoff-aware retrieval index

Expected output:

- episode-aware severe recall
- episode-aware top-K precision
- false optimism audit against packet-only eval

### Experiment B — mixed-train / strict-eval

Goal:

- 判断 `unknown_time` legacy rows 作为 train-only 辅助监督是否有收益

Method:

- train: packet-linked + legacy unlinked rows
- eval: packet-linked only
- compare with Experiment A

Expected output:

- whether auxiliary legacy rows help or hurt packet-linked eval

### Experiment C — time-aware retrieval hygiene audit

Goal:

- 验证 retrieval 是否因未来 incident 泄漏而虚高

Method:

- same eval set
- compare:
  - unrestricted retrieval index
  - cutoff-aware retrieval index

Expected output:

- leakage delta
- whether current retrieval scores are overly optimistic

### Experiment D — temporal overlay completeness audit

Goal:

- 统计各 supervision 文件中 `timestamp_quality` 的覆盖率

Expected output:

- `% exact_window_time`
- `% exact_time_inherited`
- `% coarse_text_time`
- `% unknown_time`

## 7.2 P1 experiments

### Experiment E — episode grouping ablation

- compare packet-only split vs episode-aware split
- quantify optimism gap

### Experiment F — recency-aware retrieval weighting

- add decay based on `historical_incident.derived_ts_end`
- compare retrieval rank / teacher routing impact

### Experiment G — light temporal feature enrichment

优先尝试：

- `episode_window_index`
- `episode_duration_minutes`
- `time_since_recent_deploy`
- `time_since_last_similar_incident`
- `same_service_recent_packet_count`

不建议当前直接尝试：

- full temporal backbone as primary scorer
- long-sequence autoregressive student over packet streams

---

## 8. Priority and Implementation Order

## 8.1 P0 — now

1. 建立 `temporal-lineage / timestamp_quality` 分层
2. 给所有 packet-linked 历史样本补 `derived_ts_*`
3. 继续历史离线训练，但改成 strict time-aware / episode-aware eval
4. 为 retrieval 增加 cutoff-aware compare

## 8.2 P1 — next

1. 建立 `episode-index`
2. 引入 recency-aware retrieval weighting
3. 在 structured student / Granite 2B lane 上增加轻量 temporal features

## 8.3 P2 — later

1. temporal sidecar backend compare（`TimesFM / Chronos family`）
2. packet `temporal` section 扩展
3. future escalation / persistence risk lane

---

## 9. Final Recommendations

### 9.1 What is true now

- 当前 repo 已经有足够时间锚点做有效 temporal alignment
- 当前不具备多周/多月严格 machine-timestamped training set
- 当前最该补的是 temporal lineage discipline，而不是先补一个大时序模型

### 9.2 What the team should do next

- 把“有没有时间”问题，升级成“时间质量是否足够支持当前用途”问题
- 把训练、检索、teacher、eval 全部接到同一 `timestamp_quality` contract
- 把 official gate 与 offline experiment 分开：
  - offline 历史训练可继续前跑
  - `DV2` 的真实 next-date schema gate 仍保持原约束

### 9.3 Final architecture advice

当前 `fixit` 的正确 temporal 演进顺序应冻结为：

`temporal alignment -> episode-aware eval -> recency-aware retrieval / light temporal features -> temporal sidecar`

而不是：

`直接上长序列模型 -> 再回头补时间纪律`
