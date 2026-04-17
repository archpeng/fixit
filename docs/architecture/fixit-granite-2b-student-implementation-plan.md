# fixit Granite 2B student implementation plan

- Status: `chosen-current-implementation-track`
- Scope: `current local-small-model implementation choice / Granite 2B technical design / data flow / training flow / runtime gating`
- Repo: `/home/peng/dt-git/github/fixit`
- Last updated: `2026-04-17`
- Primary reader: 后续负责把 `Granite 2B` 落成 first operational local student 的执行者

---

## 1. Decision Summary

### 1.1 Chosen current implementation track

在已冻结的 long-term strategy memo 基础上，`fixit` 当前 small-model implementation choice 明确选为：

- model family: `ibm-granite/granite-3.3-2b-instruct`
- role: `first operational local student / cost-latency floor candidate`
- teacher stays: `Gemma4 26B` on `gpu-node`
- training path stays:
  - `DAPT`
  - `SFT`
  - `ranking`（延后到 wave-2，不在第一波一开始就实现）
  - `calibration`
- deployment shape stays:
  - **先做 offline shadow / replay scorer**
  - **不直接进入 always-on runtime primary lane**

### 1.2 Why this choice is valid even if Granite 2B is not the highest-ceiling candidate

当前用户已明确选择 `Granite 2B`，本计划因此不再讨论“是否改回 Qwen / Phi 作为当前 implementation 选择”，而是冻结一个符合 repo 当前现实的工程路线：

- 用 `Granite 2B` 快速建立第一套真实 local student 数据与训练闭环
- 用它回答“一个真正便宜的 local student 是否已足够有用”
- 保留未来升级到更高 ceiling base 的迁移权，而不把这次选择绑成终局

### 1.3 Explicit accepted tradeoff

选择 `Granite 2B` 意味着接受以下 tradeoff：

- 相比 `Qwen/Qwen3-4B-Instruct-2507`，长期 semantic headroom 更低
- 相比 `microsoft/Phi-3.5-mini-instruct`，社区微调 cookbook 更少
- 对 teacher distillation 的吸收上限可能更早出现 ceiling

但换来：

- 更低训练/推理成本
- 更容易先做出 first deployable local student
- 更适合作为 `dense scorer floor candidate`
- 更适合在当前 `review gap / teacher volume / schema stability` 仍是主阻断时先跑通完整实现链路

---

## 2. Current truths that govern this plan

## 2.1 Current repo truth

当前 repo 已经有：

- `incident packet` 作为 canonical decision unit
- replay refresh / packet build / retrieval / cheap student / teacher / eval / calibration 基础设施
- 当前 next-stage runtime 默认仍是：
  - `cheap dense scorer -> teacher -> human gate`
- local-small-model branch 当前尚未 admitted into runtime primary lane

因此 Granite 2B 计划必须满足：

- 先接入为 **experimental student arm**
- 不破坏现有 structured baseline control arm
- 不破坏 `Gemma4 teacher` 和 `human gate` 的主保护线

## 2.2 Current infrastructure truth

当前已知硬件/服务分工：

### Local host

- host: `spark-b2a9`
- GPU: `1 x NVIDIA GB10`
- recommended role in this plan:
  - Granite 2B training
  - Granite 2B offline inference / replay scoring
  - adapter export / eval

### Remote teacher host

- alias: `gpu-node`
- host: `192.168.4.239`
- access: `ssh gpu-node` 已可免密登录
- current service:
  - `Gemma4 26B` via `vLLM`
  - endpoint: `http://192.168.4.239:8000/v1`
- current role in this plan:
  - teacher judgement
  - distillation source
  - hard-case preference source

### Consequence

本计划不要求：

- 立刻在 `gpu-node` 上再开第二个 always-on student service
- 立刻让 Granite 2B 和 Gemma4 teacher 共享同一远端 runtime

当前最稳妥方案是：

- `Gemma4 26B` 保持远端 teacher
- `Granite 2B` 先在本地 `spark-b2a9` 做训练与 offline shadow scoring

---

## 3. Role split in the Granite track

## 3.1 `Gemma4 teacher`

固定职责：

- hard-case judgement
- teacher rubric
- action recommendation on ambiguous cases
- pairwise preference generation
- hard-negative diagnosis

不承担：

- 全量 dense scoring
- current runtime student replacement

## 3.2 `Granite 2B student`

固定职责：

- packet-level dense first-pass scoring
- `severity_band` candidate
- `needs_teacher` prediction
- `recommended_action` candidate
- `confidence` / `reason_codes` candidate

不承担：

- 全量自由 prose explanation
- 替代 teacher 做复杂跨信号仲裁
- 直接替代 human final gate

## 3.3 Existing structured baseline control arm

保留现有 control arm：

- `fixit_ai/student.py`
- `scripts/train_student.py`

该 arm 用于：

- 对照 Granite 2B 增益
- 确认当前增益来自 Granite 2B，而不是数据分布变化
- 给 rollback 保留低复杂度回退面

---

## 4. Why Granite 2B is the right `current` implementation choice

## 4.1 It matches the current bottleneck better than a higher-ceiling model

当前 repo 阻断仍偏向：

- `review gap`
- `teacher volume`
- `schema stability`
- not yet `semantic ceiling`

因此当前更重要的是：

- 快速把 local student training/eval/shadow loop 跑通
- 更低成本地增加 experiment count
- 更快得到真实 deployment feedback

而不是：

- 一上来就押更大、更重、更高 ceiling 的 base

## 4.2 Granite 2B is still architecturally suitable

基于当前已确认 config：

- `GraniteForCausalLM`
- ~`2B` class
- `32 Q heads / 8 KV heads` → `GQA`
- `131072` context
- `Apache-2.0`
- standard HF config

这意味着它对 `fixit` 的 dense scorer 目标仍然合格：

- text-first
- enough context
- GQA 对 batch/kv-cache 友好
- serving and quantization potential reasonable

## 4.3 It is the best floor-candidate for answering the immediate question

当前最值得回答的工程问题不是：

- “最强 small base 是谁？”

而是：

- “一个真正便宜的 local student 是否已经能为 fixit 带来真实 triage 价值？”

`Granite 2B` 是这个问题最好的 current probe。

---

## 5. Accepted losses and explicit mitigations

## 5.1 What we lose by choosing Granite 2B now

### Loss A — lower semantic ceiling

可能表现为：

- 对 rule-missed severe packet 的 recall ceiling 更早出现
- teacher escalation 降不下去
- reason_codes 粗糙
- ranking quality 不如 4B-class candidate

### Loss B — lower teacher distillation capacity

可能表现为：

- teacher rubrics 学不全
- preference signals 吸收不如 4B-class candidate
- harder to compress complex hard cases into a 2B student

### Loss C — weaker community cookbook

可能表现为：

- 可参考的 LoRA/QLoRA recipe 较少
- 社区 benchmark / tuning stories 较少
- 需要更依赖 repo 自己的 eval discipline

## 5.2 Why these losses are acceptable now

这些损失在当前阶段可接受，因为：

- 当前瓶颈不是 small-model semantic ceiling
- 当前更需要 first operational student 的完整闭环
- control arm 仍保留
- 未来升级到 `Qwen3-4B` 仍是开放迁移路径

## 5.3 Explicit migration triggers

若出现下列任一情况，应准备从 Granite 2B 升级到 higher-ceiling base（优先 `Qwen3-4B`）：

1. Granite 2B 在 replay/shadow 上无法把 teacher escalation 压到目标带内
2. Granite 2B 的 severe recall / top-K precision 经 calibration 后仍明显低于 control arm + teacher path
3. Granite 2B 在 hard-case distillation 上长期停滞
4. `reason_codes` 与 `action` 的可用性不足，导致 human gate 无法稳定使用
5. 数据飞轮已增长，current bottleneck 变成 semantic headroom 而不是 data/review gap

---

## 6. Technical implementation shape

## 6.1 Governing principle

Granite 2B 轨道必须服从当前 repo 主约束：

- `incident packet` remains canonical
- first implementation is **offline shadow scorer**, not direct primary runtime replacement
- training target is still structured triage output
- no raw-log-only modeling

## 6.2 Model starting point

当前 starting checkpoint 冻结为：

- `ibm-granite/granite-3.3-2b-instruct`

当前不采用：

- `granite-3.3-2b-base` 作为第一波 starting point

原因：

- 当前数据量和 rollout maturity 还不值得先从 base-only 路线增加不必要不稳定性
- instruct checkpoint 更容易直接对齐到 `JSON structured triage` 输出
- 更适合当前第一波 `DAPT + SFT` 工程闭环

## 6.3 First-wave training style

第一波训练采用：

- `LoRA / QLoRA first`
- 不做 full fine-tune first
- 不一开始就引入 preference optimization / DPO / RL-style loop

原因：

- 目标是先快速落成本地 student 闭环
- 当前不是追求极限 benchmark，而是追求可持续迭代和低回滚成本

---

## 7. Repo changes required

## 7.1 New config files

建议新增：

- `configs/models/granite-2b-student.yaml`
- `configs/training/granite-2b-dapt.yaml`
- `configs/training/granite-2b-sft.yaml`
- `configs/training/granite-2b-calibration.yaml`

### `configs/models/granite-2b-student.yaml`

最小字段建议：

```yaml
model_id: ibm-granite/granite-3.3-2b-instruct
family: granite-2b-student
mode: offline-shadow
max_input_tokens: 8192
max_output_tokens: 256
dtype: bfloat16
quantization: null
adapter_method: qlora
teacher_endpoint: http://192.168.4.239:8000/v1
teacher_model: gemma-4-26B-A4B-it
```

### `configs/training/granite-2b-dapt.yaml`

```yaml
stage: dapt
dataset: data/train/granite/packet_text_corpus.jsonl
sequence_length: 4096
learning_rate: 1e-4
epochs: 1
lora_r: 32
lora_alpha: 64
lora_dropout: 0.05
```

### `configs/training/granite-2b-sft.yaml`

```yaml
stage: sft
dataset: data/train/granite/sft_examples.jsonl
sequence_length: 4096
learning_rate: 5e-5
epochs: 2
lora_r: 64
lora_alpha: 128
lora_dropout: 0.05
```

### `configs/training/granite-2b-calibration.yaml`

```yaml
method: temperature_then_threshold
target_metrics:
  severe_recall_floor: 1.0
  top_k_precision_floor: 1.0
  teacher_escalation_ceiling: 0.15
```

## 7.2 New Python modules

建议新增：

- `fixit_ai/student_packet_render.py`
- `fixit_ai/granite_datasets.py`
- `fixit_ai/granite_teacher_distill.py`
- `fixit_ai/granite_student.py`
- `fixit_ai/granite_eval.py`
- `fixit_ai/granite_calibration.py`

### Responsibilities

#### `student_packet_render.py`

负责把 packet 渲染成 deterministic text / chat input。

#### `granite_datasets.py`

负责生成：

- DAPT corpus rows
- SFT rows
- ranking rows（wave-2）
- calibration rows

#### `granite_teacher_distill.py`

负责：

- 调用 `Gemma4 teacher`
- 生成 `teacher_supervision`
- 生成 hard-case preferences

#### `granite_student.py`

负责：

- 载入 Granite adapter
- 对 packet 批量推理
- 输出 structured triage JSON candidate

#### `granite_eval.py`

负责：

- replay/shadow compare
- top-K / severe recall / teacher escalation readout

#### `granite_calibration.py`

负责：

- score normalization
- threshold search
- confidence bucket report

## 7.3 New scripts

建议新增：

- `scripts/build_packet_text_corpus.py`
- `scripts/build_teacher_supervision.py`
- `scripts/train_granite_dapt.py`
- `scripts/train_granite_sft.py`
- `scripts/run_granite_student.py`
- `scripts/evaluate_granite_shadow.py`
- `scripts/build_granite_calibration_report.py`

---

## 8. Data products and contracts

## 8.1 Packet rendering contract

student 输入必须来自 packet 渲染，不得直接来自 raw logs dump。

### Recommended rendered shape

```text
[packet]
packet_id=ipk_xxx
service=g-crm-campaign
operation=ADCService/Compile
env=prod
window=2026-04-16T11:40:00Z..2026-04-16T11:45:00Z

[metrics]
error_rate_delta=0.10
p95_delta=0.59
qps_delta=0.21
trace_error_ratio=0.74

[logs]
top_template_1=campaign compiler returned retryable internal server error after template expansion
novelty_1=0.97
count_1=3

[topology]
tier=tier2
owner=growth-campaign-oncall
repos=g-crm-campaign,ad-compiler
blast_radius_score=0.68

[rules]
fired=[]
rule_missed=true

[retrieval]
ref_1=inc-compile-500 severe page_owner
ref_2=inc-compile-materialization severe page_owner

[memory]
recent_incidents=INC-1422,INC-1198

[task]
Return JSON with severity_band needs_teacher recommended_action reason_codes confidence_band.
```

## 8.2 DAPT corpus

### Output path

- `data/train/granite/packet_text_corpus.jsonl`

### Row shape

```json
{
  "packet_id": "ipk_w004",
  "text": "<rendered packet text>",
  "source": "incident_packet"
}
```

DAPT corpus 允许包含：

- packet text
- packet + retrieval ref summary
- packet + teacher rationale summary
- packet + outcome summary

## 8.3 SFT corpus

### Output path

- `data/train/granite/sft_examples.jsonl`

### Row shape

```json
{
  "packet_id": "ipk_w004",
  "input_text": "<rendered packet text>",
  "target_json": {
    "severity_band": "P1",
    "needs_teacher": true,
    "recommended_action": "page_owner",
    "reason_codes": [
      "rule_missed_high_score",
      "novel_template",
      "similar_to_severe_incident"
    ],
    "confidence_band": "medium"
  },
  "label_source": "teacher_rubric",
  "gold_weight": 0.75
}
```

### Label source rule

优先级不变：

1. `human outcome`
2. `production outcome`
3. `teacher rubric`
4. `rule`

## 8.4 Ranking corpus — wave 2 only

### Output path

- `data/train/granite/ranking_pairs.jsonl`

### Row shape

```json
{
  "pair_id": "pair_001",
  "left_packet_id": "ipk_w004",
  "right_packet_id": "ipk_w005",
  "preferred": "left",
  "preference_source": "teacher_or_human",
  "reason": "left should rank higher in triage queue"
}
```

### Rule

ranking 在 Granite 2B track 中是 **wave-2 enhancement**，不要求第一波必须先上线。

---

## 9. Training flow for the Granite track

## 9.1 Wave 0 — data readiness

必须先落：

1. packet deterministic rendering
2. teacher supervision export
3. label-source provenance export
4. heldout replay split for calibration

### Exit gate

- `packet_text_corpus.jsonl` 已稳定生成
- `sft_examples.jsonl` 至少已有可跑的小规模样本
- teacher / human / outcome provenance 没丢

## 9.2 Wave 1 — `DAPT`

### Goal

让 Granite 2B 先适应 `fixit` 的 packet-native distribution。

### Implementation rule

- use `granite-3.3-2b-instruct`
- LoRA/QLoRA first
- objective = causal continuation on packet corpus
- do not mix massive unrelated corpora

### Output

- `artifacts/models/granite-2b/dapt-adapter/`
- `data/eval/granite/dapt-readout.json`

### Exit gate

- DAPT run reproducible
- no obvious degradation in packet formatting comprehension
- adapter export/load works on local host

## 9.3 Wave 1.5 — teacher-distill refresh

### Goal
n
扩大 Granite 2B 的 task supervision，不直接依赖 sparse gold-only labels。

### What to build

- teacher requests from hard cases
- teacher structured outputs
- teacher-to-SFT transformed rows

### Output

- `data/train/granite/teacher_supervision.jsonl`
- merged into `sft_examples.jsonl`

## 9.4 Wave 2 — `SFT`

### Goal

让 Granite 2B 输出 fixit 需要的结构化 triage JSON。

### First-wave target fields

第一波只要求：

- `severity_band`
- `needs_teacher`
- `recommended_action`
- `reason_codes`
- `confidence_band`

### Explicit non-goal for first wave

不要求第一波就做到：

- long-form explanation quality最好
- complex chain-of-thought
- full pairwise ranking perfection

### Output

- `artifacts/models/granite-2b/sft-adapter/`
- `data/eval/granite/sft-shadow-predictions.jsonl`

## 9.5 Wave 3 — calibration

### Goal

把 Granite 2B raw outputs 收紧成可以和 control arm / teacher lane 比较的 calibrated signals。

### Required outputs

- `granite_score`
- `granite_confidence`
- threshold proposal
- teacher escalation simulation

### Output path

- `data/eval/granite/calibration-report.json`
- `data/eval/granite/calibration-report.md`

## 9.6 Wave 4 — ranking enhancement (only if needed)

### Admission rule

只有当下列任一条件成立，才进入 ranking enhancement：

- SFT-only 版本的 top-K ordering 不稳定
- teacher escalation 仍偏高
- severe recall 不差，但 queue ordering 价值不足

### Implementation choice

优先：

- pairwise ranking fine-tune on top of SFT adapter

暂不引入：

- RLHF / DPO / PPO style training

---

## 10. Shadow evaluation design

## 10.1 Three-arm comparison

Granite 2B track 必须做三臂对照：

1. current structured baseline
2. Granite 2B student
3. Granite 2B + teacher gated path

## 10.2 Core metrics

必须保留：

- severe recall
- top-K precision
- teacher escalation rate
- fallback burden
- missed severe count
- action confusion matrix

## 10.3 Granite-specific readout

额外输出：

- Granite JSON parse success rate
- Granite reason_codes usability rate
- Granite confidence bucket stability
- Granite vs control arm disagreement set

## 10.4 Protection bars

沿用当前 repo bars：

- success recall floor = `1.0`
- success top-K precision floor = `1.0`
- success teacher escalation ceiling = `0.15`
- rollback precision trigger = `0.95`

解释：

- Granite 2B 不能因为更便宜，就允许在 replay/shadow 上明显退化

---

## 11. Serving and runtime policy

## 11.1 Current policy

Granite 2B 第一阶段 **不做 always-on primary runtime service**。

当前推荐模式：

- local offline batch scorer
- replay/shadow output artifact producer
- optional ad-hoc local endpoint only for testing

## 11.2 Why not serve immediately

因为当前 repo 总体仍未过：

- local model admission gates
- latency budget freeze
- rollback plan freeze
- schema stability window

因此 Granite 2B track 的第一目标不是“开服务”，而是：

- 先证明 cheap local student 在当前数据条件下是否有真实 triage 价值

## 11.3 Future serving target once admitted

一旦 replay/shadow 过线，再考虑：

- on `spark-b2a9` serve Granite 2B locally
- expose bounded internal endpoint for batch scoring
- keep Gemma4 remote teacher unchanged

建议最终 runtime shape：

```text
packet batch
  -> Granite 2B local scorer
  -> if needs_teacher/high-risk then Gemma4 teacher on gpu-node
  -> human gate on escalations
```

---

## 12. Concrete implementation order

## Slice G0 — packet render + dataset contracts

### Deliverables

- `fixit_ai/student_packet_render.py`
- `scripts/build_packet_text_corpus.py`
- `data/train/granite/packet_text_corpus.jsonl`
- `data/train/granite/sft_examples.jsonl`

### Exit gate

- deterministic render exists
- SFT rows reproducibly generated

## Slice G1 — teacher supervision export

### Deliverables

- `fixit_ai/granite_teacher_distill.py`
- `scripts/build_teacher_supervision.py`
- `data/train/granite/teacher_supervision.jsonl`

### Exit gate

- teacher-derived labels merge cleanly with existing provenance

## Slice G2 — DAPT adapter

### Deliverables

- `scripts/train_granite_dapt.py`
- `artifacts/models/granite-2b/dapt-adapter/`
- `data/eval/granite/dapt-readout.json`

### Exit gate

- local load/inference works on `spark-b2a9`

## Slice G3 — SFT adapter

### Deliverables

- `scripts/train_granite_sft.py`
- `fixit_ai/granite_student.py`
- `scripts/run_granite_student.py`
- `data/eval/granite/sft-shadow-predictions.jsonl`

### Exit gate

- JSON parse success acceptable
- shadow scoring end-to-end completes

## Slice G4 — calibration + shadow compare

### Deliverables

- `fixit_ai/granite_calibration.py`
- `scripts/build_granite_calibration_report.py`
- `scripts/evaluate_granite_shadow.py`
- `data/eval/granite/calibration-report.json`
- `data/eval/granite/shadow-compare.json`

### Exit gate

- Granite 2B can be judged against current control arm with frozen metrics

## Slice G5 — ranking enhancement (conditional)

### Deliverables

- `data/train/granite/ranking_pairs.jsonl`
- ranking adapter artifacts
- revised shadow compare

### Admission

- only if G4 shows queue-ordering weakness with otherwise acceptable recall

---

## 13. Final recommendation

当前 `fixit` 的 Granite 2B 具体落地技术方案应冻结为：

- `Granite 2B` 作为 first operational local student / floor candidate
- `Gemma4 26B` 继续作为 remote teacher / distillation source
- 本地 `spark-b2a9` 单卡 GB10 先承担 Granite 训练与 offline shadow scoring
- 先落 `packet render -> teacher supervision -> DAPT -> SFT -> calibration`
- ranking enhancement 放到 wave-2，不在第一波强行一起上
- structured baseline control arm 保留，直到 Granite 2B 在 replay/shadow 上证明真实增益
- 若 Granite 2B 后续 hit ceiling，再迁移到 `Qwen3-4B`，而不是在当前阶段一开始就放弃低成本 probe

一句话总结：

> 当前不是用 `Granite 2B` 赌终局，而是用它最低成本地把 `fixit` 的 local-student 训练、评测、shadow、校准和 teacher 协同链路真正跑通；一旦它不够，再基于同一套数据与评测面升级到更高 ceiling base。 
