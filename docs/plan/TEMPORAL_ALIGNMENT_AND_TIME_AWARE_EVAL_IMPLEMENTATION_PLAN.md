# TEMPORAL_ALIGNMENT_AND_TIME_AWARE_EVAL_IMPLEMENTATION_PLAN

- Status: closed
- Family: `TEMPORAL_ALIGNMENT_AND_TIME_AWARE_EVAL_IMPLEMENTATION`
- Created: 2026-04-17
- Plan type: repo-global temporal alignment / time-aware eval execution pack
- Primary handoff: `execute-plan`
- Trigger source: user-directed focus shift after temporal strategy docs landed and were pushed
- Source anchors:
  - `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`
  - `docs/architecture/fixit-temporal-model-sidecar-design.md`
  - `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL_STATUS.md`
  - `data/samples/incident-packets.jsonl`
  - `data/eval/historical_incidents.jsonl`
  - `data/eval/training_examples.jsonl`
  - `data/eval/outcomes.jsonl`
  - `data/eval/manual_teacher_judgements.jsonl`
  - `AGENTS.md`

---

## 1. Goal

把已经落地的 temporal strategy doc 压成真实可执行代码、tests、scripts、artifacts，使 repo 具备：

1. temporal lineage / `timestamp_quality` SSOT artifact
2. packet-linked 历史监督样本的派生时间对位能力
3. `episode-aware split` 与 `time-aware eval` 的最小可执行实现
4. strict historical offline experiment lane，不跳过 `DV2` 的真实 next-date gate

本 family 的目标不是“先上时序模型”，而是把当前 repo 的时间纪律补成可验证基础设施。

---

## 2. In Scope

- `fixit_ai` 内新增 temporal alignment / episode grouping / time-aware eval 支撑代码
- 新 script-backed artifacts，例如：
  - `data/eval/temporal-lineage.jsonl`
  - `data/eval/temporal-alignment-summary.json`
  - `data/eval/episode-index.json`
  - temporalized replay/eval overlays
  - time-aware offline eval summary
- 对 packet-linked history 的 `derived_ts_*` / `timestamp_quality` overlay
- retrieval cutoff hygiene for strict eval lane
- leave-one-episode-out or equivalent bounded episode-aware eval
- `PLAN/STATUS/WORKSET` closeout and successor routing

---

## 3. Out of Scope

- 不推进 `DV2` schema next-date gate 本身
- 不把历史离线训练结果当作 schema gate 替代证据
- 不引入 `TimesFM / Chronos family` backend
- 不把 temporal sidecar 接入 runtime primary lane
- 不启动 Granite 2B implementation family
- 不做多周/多月 forecasting-first system

---

## 4. Entry Criteria

当前前置已满足：

- temporal strategy docs 已 landed and pushed
- current repo 已有 packet-level exact window time
- current packet-linked history 已可通过 `packet_id` / `source_packet_ids` 建立时间继承
- current active daily residual family 的 `DV2` 明确被真实 next-date gate 阻塞，无法在同日伪造推进
- user 明确要求立即执行 temporal alignment P0，并采用 `execution -> review -> replan` + TDD

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `TW1_TEMPORAL_LINEAGE_CONTRACT_AND_ARTIFACT` | 先把时间锚点和 `timestamp_quality` 落成代码与 artifact | temporal lineage builder, summary artifact, tests | packet/outcome/training/incident time mapping is script-backed |
| `TW2_PACKET_LINKED_TEMPORAL_OVERLAYS` | 把 packet-linked history 变成可直接消费的 temporal overlays | temporalized replay/eval JSONL overlays, completeness audit | packet-linked rows all carry derived time + quality |
| `TW3_EPISODE_AWARE_SPLIT_AND_TIME_AWARE_EVAL` | 引入 episode grouping、strict split 与 cutoff-aware eval | episode index, time-aware eval script/artifact, tests | strict historical offline experiment lane is runnable |
| `TW4_CLOSEOUT_AND_SUCCESSOR_DECISION` | family closeout and routing | closeout docs, status/workset final truth, validation evidence | family can be resumed or handed off without ambiguity |

---

## 6. Verification Ladder

### Layer A — active wave proof

每个 wave 都必须先 fail-first，再补实现：

- targeted unittest fail-first
- code / script implementation
- targeted unittest green

### Layer B — script-backed proof

每个 accepted wave 至少要跑：

- 对应新增 script
- artifact readback

### Layer C — regression proof

每个 accepted wave 默认补跑：

```bash
python3 -m unittest discover -s tests -v
```

若 wave 会触达 replay / packet / retrieval / eval truth，补跑：

```bash
python3 scripts/run_hardening_pipeline.py
```

或本 family 专属 temporal script lane。

---

## 7. Risks / Blockers

1. 当前 exact-time coverage集中在 packet lane，legacy supervision rows 仍有 `unknown_time`
2. 同一 incident family 可能跨多个不连续 windows，episode grouping 若过于机械会失真
3. retrieval strict cutoff compare 可能显著暴露当前 optimistic bias
4. 必须防止 temporal workstream 偷偷变成 `DV2` gate bypass narrative
5. 当前 family 不能破坏既有 packet-centric runtime 主线

---

## 8. Stop Conditions

出现下列任一情况时，必须停下 review / replan：

- 需要伪造时间才能补齐 overlay
- 需要把 `coarse_text_time` 冒充 `exact timestamp`
- `episode-aware` 定义出现多套同等主导方案，无法单刀推进
- 实现想绕过 packet canonical unit 改成 raw log temporal modeling
- 历史离线实验结果被错误用于放行 `DV2` / rerun admission

---

## 9. Exit Criteria

本 family closeout 至少满足：

1. `temporal-lineage` artifact script-backed and reproducible
2. packet-linked history 的派生时间 overlay 已真实落地
3. `timestamp_quality` taxonomy 已进入代码与 artifact contract
4. 最少一条 strict `episode-aware / time-aware` offline eval lane 可运行
5. `PLAN/STATUS/WORKSET` 已写清 residual 与 successor

---

## 10. Initial Ordering

默认执行顺序：

1. `TW1.S1_TEMPORAL_LINEAGE_CONTRACT_AND_ARTIFACT`
2. `TW2.S1_PACKET_LINKED_TEMPORAL_OVERLAYS_AND_COMPLETENESS_AUDIT`
3. `TW3.S1_EPISODE_AWARE_SPLIT_AND_TIME_AWARE_EVAL`
4. `TW4.S1_CLOSEOUT_AND_SUCCESSOR_DECISION`
