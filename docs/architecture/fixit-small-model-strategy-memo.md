# fixit small model strategy memo

- Status: `proposed-strategy-ssot`
- Scope: `local small student strategy / base-model adaptation / teacher-student split / future autoresearch admission`
- Repo: `/home/peng/dt-git/github/fixit`
- Last updated: `2026-04-17`
- Primary reader: 后续负责 `student` 路线实现、训练、蒸馏、评测与 rollout 的执行者

---

## 1. Decision Summary

### 1.1 Chosen mainline

`fixit` 的本地小模型主路线冻结为：

- 选择 **small base model adaptation**，不走当前阶段的 `from-scratch` / `autoresearch-first` 主线
- 先从 **text-first / small parameter / easy-to-serve** 的 base model 开始
- 把当前 `Gemma4 26B` 运行面固定为 **teacher / distillation source**，不把它当 dense first-pass student
- 训练方法采用：
  - `DAPT`（domain-adaptive pretraining）
  - `SFT`（结构化任务微调）
  - `pairwise/listwise ranking`
  - `calibration + thresholding`
- student 最终输出必须仍是 **结构化 triage signals**，不是自由 prose

### 1.2 Explicit non-chosen mainlines

当前不采用下列路线作为主线：

- 直接用 `/home/peng/dt-git/autoresearch` 反复从零研究并训练专用小模型
- 直接把 `Gemma4 26B` 微调成第一层 dense student
- 把多模态小模型作为当前第一候选 student base
- 不经过数据/蒸馏/校准，仅靠 prompt engineering 把本地模型硬堆成 student

### 1.3 Important status caveat

本 memo **冻结的是将来进入 local small model family 之后的正确方向**，不是说当前 repo 已经到达 implementation admission。

当前仓库内已知事实仍然是：

- `keep_classic_baseline` 仍是 `preferred_now`
- `small_encoder_classifier` 仍是 `future_candidate`
- `small_instruct_reranker` 仍是 `defer`
- 当前主阻断仍偏向：
  - `review gap`
  - `teacher volume`
  - `schema stability`
  - `deployment budget / latency / rollback` 未冻结

因此本 memo 服务于：

- 未来进入 small-model implementation family 时不走偏
- 提前冻结 teacher/student 边界、candidate order 与训练方法
- 避免后续在“自训小模型 vs 微调现成基座”之间反复摇摆

---

## 2. Why mainline chooses `base-model adaptation`

## 2.1 Project objective mismatch: `autoresearch` optimizes the wrong problem first

`autoresearch` 当前默认目标是：

- `single-GPU`
- `fixed 5-minute budget`
- 优化 `val_bpb`
- 研究预训练架构 / 训练 recipe

而 `fixit` student 的真实目标是：

- `incident packet` triage
- `severity band`
- `needs_teacher`
- `recommended_action`
- `priority ranking`
- `confidence / novelty`

这意味着：

- `autoresearch` 当前优化的是 `next-token pretraining`
- `fixit` 需要的是 `packet-native ranking / classification`

`val_bpb` 变好，**不等于** severe recall、top-K precision、teacher escalation rate 变好。

所以在当前阶段，把 `autoresearch` 当主线，会先把资源投到一个与目标函数不一致的方向上。

## 2.2 `fixit` 的长期复利资产在数据飞轮，而不在 small foundation model ownership

`fixit` 的真正长期资产是：

- `incident packet` contract
- `packet -> retrieval -> student -> teacher -> human outcome` 数据飞轮
- `teacher rubric` 与 `human outcome` 的 provenance
- `calibration / threshold / rollback` 机制
- `service -> topology -> owner -> repo` routing truth

不是：

- 自己从零维护一套小 foundation model 训练栈

对本项目来说，更符合 `Bitter Lesson` 的长期投入方向是：

- 更多 packet
- 更多 hard-case judgement
- 更多真实 outcome
- 更好的蒸馏
- 更好的 ranking / calibration

而不是过早投入到：

- 自主预训练 recipe 搜索
- tokenizer / architecture 从零演化
- 单看语言建模指标的自训循环

## 2.3 Data efficiency strongly favors adaptation over from-scratch training

当前 `fixit` 已知事实显示：

- severe miss 还没有清楚地表现成 semantic ceiling
- 当前 hard case 的 dominant gap 更偏 `review gap`
- label / teacher / schema / pilot breadth 仍在积累期

在这种阶段：

- `from-scratch` 或 `autoresearch-first` 的 sample efficiency 太差
- `small base model + DAPT + SFT + ranking` 对有限高价值数据更友好

也就是说，当前最稀缺的资源不是“再多做一些 generic LM 训练 step”，而是：

- high-value packet corpus
- teacher-reviewed hard cases
- human-confirmed outcomes

## 2.4 Deployment and rollback economics favor smaller adapted bases

`fixit` student 的运行定位是：

- cheap
- dense
- first-pass
- high-throughput
- rollback-friendly

因此 student 需要：

- 小参数量
- text-first
- 显存与延迟更可控
- 便于量化、LoRA、A/B、canary

相比之下，`from-scratch` 自训路线意味着还要同时承接：

- pretraining stability
- tokenizer / corpus / objective 设计
- base capability 回退风险
- serving / quantization / eval 兼容性

这对当前 `fixit` 来说不是最优主线。

## 2.5 Existing repo evidence already points to this direction

根据当前 repo 内文档真相：

- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_MODEL_OPTION_MATRIX.md`
  - `keep_classic_baseline` = `preferred_now`
  - `small_encoder_classifier` = `future_candidate`
  - `small_instruct_reranker` = `defer`
- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_EVIDENCE_AUDIT.md`
  - 当前阻断主要不是 semantic-failure ceiling
- `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_DEPLOYMENT_REVIEW.md`
  - local model deployment readiness = `not_ready`

所以主线选择 `base-model adaptation`，既符合项目目标，也与 repo 当前证据一致。

---

## 3. Current truths that govern this memo

## 3.1 Internal repo truths

当前已冻结的 repo truth：

- canonical decision unit = `incident packet`
- next-stage runtime default =
  - `bounded telemetry -> incident packet -> cheap dense scorer -> teacher -> human gate -> outcomes/labels`
- 当前不推荐直接把本地小模型放入主运行面
- 当前 small-model family 的最佳 immediate action 仍是：
  - 继续补 `replay breadth`
  - 继续补 `teacher reviewed volume`
  - 继续补 `schema stability`
  - 继续补 `deployment budget / rollback bars`

## 3.2 External environment truth available now

当前已存在的可复用 teacher 环境：

- host alias: `gpu-node`
- host: `192.168.4.239`
- access: 本地 `ssh gpu-node` 已可免密登录
- service: `Gemma4 26B` via `vLLM`
- endpoint: `http://192.168.4.239:8000/v1`
- model: `gemma-4-26B-A4B-it`
- current mode: `text-only`
- current runtime: `tensor-parallel-size=4`, `max-model-len=2048`

这意味着：

- 本地 teacher / distillation source 已经存在
- 未来 small student 主线不需要先解决“有没有 teacher runtime”这个问题

## 3.3 Consequence

对 `fixit` 而言，当前正确动作不是：

- 先去发明新的小 foundation model

而是：

- 把现有 `Gemma4 26B teacher` 用起来
- 让 small student 从更小、更便宜、更易部署的 text-first base 上长出来

---

## 4. `Gemma4 teacher` vs `small student` role split

## 4.1 Role split overview

| Layer | Primary role | Cost profile | Main input | Main output | Current status |
|---|---|---:|---|---|---|
| `Gemma4 26B teacher` | hard-case judgement / distillation source | high | compact packet + retrieval refs + conflict context | rubric / action / rationale / pairwise preference | available now |
| `small student` | dense first-pass triage | low | compact packet | severity / needs_teacher / route / ranking / confidence | future implementation |

## 4.2 `Gemma4 26B teacher` responsibilities

`Gemma4 teacher` 只负责：

- 规则与 baseline 冲突样本
- 高 novelty 样本
- 高 blast radius 样本
- low-confidence student 样本
- 需要跨 metrics/logs/traces/retrieval 聚合解释的 hard case
- 为 small student 提供蒸馏信号

推荐输出形态：

- `teacher_judgement`
- `recommended_action`
- `severity band`
- `reason_codes`
- `pairwise preference`
- `hard-negative / false-positive diagnosis`

明确不让 teacher 负责：

- 全量 packet 密集扫描
- 取代 cheap scorer 成为第一层全量判官
- 直接把 teacher prose 当 gold truth

## 4.3 `small student` responsibilities

`small student` 只负责：

- 全量 packet dense scoring
- `needs_teacher` 判定
- `severity band` 判定
- `recommended_action` 候选
- hard-case ranking
- low-cost confidence signal

推荐 student 输出 contract：

```json
{
  "packet_id": "...",
  "severity_band": "P1|P2|P3|P4",
  "severity_score": 0.0,
  "needs_teacher": true,
  "recommended_action": "observe|create_ticket|page_owner|send_to_human_review",
  "confidence": 0.0,
  "reason_codes": ["template_novelty_high", "similar_to_severe_incident"]
}
```

## 4.4 Why this split matters

这个 split 冻结了两件事：

1. `Gemma4 26B` 不再被误当成 future dense student candidate
2. student 的设计目标被固定为：`cheap / dense / structured / rollback-friendly`

---

## 5. Recommended first candidates

## 5.1 Candidate selection rubric

future small student base 候选优先满足：

- `text-first`
- `small parameter count`
- `easy to serve`
- `easy to LoRA / QLoRA`
- `chat/instruction capability exists, but not multimodal-heavy`
- `deployment complexity lower than Gemma4 teacher`
- `works well with structured JSON-style outputs`

## 5.2 Recommended order

### Current recommended order inside the small-LLM branch

1. `microsoft/Phi-3.5-mini-instruct`
2. `microsoft/phi-4`（若第一候选 ceiling 明显）
3. `google/gemma-4-E2B-it`（若 Gemma ecosystem continuity becomes more important than text-first simplicity）
4. `google/gemma-4-E4B-it`（不作为 first candidate）

## 5.3 Candidate matrix

> 注：以下体量信息来自 `2026-04-17` 时对 Hugging Face model metadata 的观察；用于比较工程适配性，不代表完整 benchmark judgement。

| Candidate | Approx size signal | Modality bias | Strengths | Weaknesses | Recommendation |
|---|---|---|---|---|---|
| `microsoft/Phi-3.5-mini-instruct` | ~`3.8B` BF16 params; storage ~`7.6GB` | text-first | 小、轻、text-only 取向更强、部署简单、适合 LoRA/QLoRA、和 packet triage 任务更贴近 | 绝对能力可能低于更大模型 | `first adaptation candidate` |
| `microsoft/phi-4` | larger; storage ~`29GB` | text-first | 能力更强，仍属于 text LLM family | 已不算很小，部署成本和 student 定位开始拉扯 | `second candidate if mini ceiling appears` |
| `google/gemma-4-E2B-it` | ~`5.1B` BF16 params; storage ~`30GB+` | any-to-any / multimodal | 和现有 `Gemma4 teacher` 家族连续性更强；license / ecosystem continuity 更好 | multimodal baggage 更重；对当前 text-only packet task 有额外复杂度 | `candidate only if Gemma alignment outweighs simplicity` |
| `google/gemma-4-E4B-it` | ~`8.0B` BF16 params; storage ~`48GB+` | any-to-any / multimodal | 可能更强 | 对“small / cheap / easy-to-serve”目标不够友好 | `not first candidate` |

## 5.4 Preferred first pick

若 future small-LLM branch 正式进入 implementation family，推荐 first pick 为：

- `microsoft/Phi-3.5-mini-instruct`

原因：

- 更符合 `text-first`
- 更符合 `small parameter`
- 更符合 `easy-to-serve`
- 对 `incident packet` 这种结构化 text triage 任务更自然
- 相比 Gemma4 E2B/E4B，更少承担多模态冗余复杂度

## 5.5 Important nuance: control arm still matters

即使 small-LLM branch 未来开启，也不应跳过控制组：

- `small_encoder_classifier`
- existing structured baseline

因为 repo 当前已有证据显示：

- `small_encoder_classifier` 比 `small_instruct_reranker` 更符合当前 future candidate 位次

因此实践上推荐：

- `control arm`: `small_encoder_classifier`
- `LLM arm`: `Phi-3.5-mini-instruct` adaptation

而不是一上来只押一个 small generative model。

---

## 6. Training pipeline: `DAPT + SFT + ranking + calibration`

## 6.1 Governing rule

small student 的训练对象仍然不是 raw logs flood，而是：

- `incident packet`
- compact retrieval refs
- topology / owner / repo summary
- teacher judgement
- human outcome

如果训练输入重新退化成：

- 全量 raw log body
- 无界 trace 文本拼接
- prompt-only heuristic narrative

则视为偏离本 memo。

## 6.2 Source -> target mapping

### Data products

| Source | Target artifact | Use |
|---|---|---|
| `incident packet` | `packet_text_corpus.jsonl` | DAPT |
| `retrieval results` + `historical_incidents` | `packet_with_refs_corpus.jsonl` | DAPT / ranking context |
| `teacher_judgements` | `teacher_supervision.jsonl` | SFT / ranking / distillation |
| `outcomes.jsonl` | `gold_labels.jsonl` | supervised labels / calibration |
| `training_examples.jsonl` | `student_supervision.jsonl` | SFT |
| `teacher disagreement / fallback cases` | `hard_case_pairs.jsonl` | pairwise ranking |

## 6.3 Step A — `DAPT`

### Goal

让 small base 先习惯 `fixit` 自己的 packet 语言、字段顺序、术语和证据结构。

### Input should look like

- packet serialization text
- packet + retrieval ref summary
- packet + outcome summary
- packet + teacher rationale summary

### DAPT corpus should include

- metrics deltas
- top log templates
- trace summary
- topology / owner / repos
- retrieval refs
- reason codes
- historical incident compressed summary

### DAPT corpus should avoid

- raw logs archive dump
- unbounded token concatenation
- massive unrelated web/code corpus mixing

### Why DAPT first

如果直接跳到 SFT：

- 模型会先学 task label
- 但不一定真正适应 packet-native distribution

先做 DAPT 的作用是：

- 降低 domain mismatch
- 改善 packet schema/术语理解
- 为后续 SFT/ranking 提供更稳底座

## 6.4 Step B — `SFT`

### Primary supervised tasks

优先训练这几类结构化任务：

1. `severity_band`
2. `needs_teacher`
3. `recommended_action`
4. `reason_codes`

### SFT target style

优先输出结构化 JSON，不优先输出长 explanation。

示例：

```json
{
  "severity_band": "P2",
  "needs_teacher": true,
  "recommended_action": "send_to_human_review",
  "reason_codes": [
    "rule_student_conflict",
    "high_blast_radius",
    "novel_template"
  ]
}
```

### Label priority

监督信号优先级保持：

1. `human outcome`
2. `production outcome`
3. `teacher rubric`
4. `rule labels`

teacher label 用作 distillation source，**不是最终 gold truth**。

## 6.5 Step C — `ranking`

### Why ranking is required

`fixit` 的 student 不是只做分类，它还要支持：

- triage queue ordering
- top-K severe candidate prioritization
- 哪些 packet 更值得用 teacher budget

所以除了 SFT 分类任务，还需要 ranking。

### Recommended ranking data

优先构造：

- `packet_a` vs `packet_b`
- 哪个更值得进 top queue
- 哪个更该升 teacher
- 哪个 action 风险更高

pairwise 来源优先：

- teacher / human disagreement review
- severe vs non-severe 同时间窗样本
- rule-hit vs rule-missed but severe 样本
- fallback / escalation / incident-confirmed 样本

### Ranking output use

ranking 不一定直接暴露给最终 API，但应进入：

- `decision_score`
- `top-K priority`
- `teacher queue selection`

## 6.6 Step D — `calibration`

### Why calibration is non-optional

student 最终要参与动作门控，所以必须可校准，不是只看 raw logits。

### Calibration targets

- severe recall
- top-K precision
- teacher escalation rate
- fallback burden
- confidence buckets / ECE-like view

### Initial operating bars

沿用 repo 当前已冻结的保护线：

- success recall floor: `1.0`
- success top-K precision floor: `1.0`
- success teacher escalation ceiling: `0.15`
- rollback precision trigger: `0.95`

解释：

- future small-model family 不允许仅靠“回答看起来更聪明”就放行
- 必须在 bounded replay 上不劣于当前 baseline

## 6.7 Promotion ladder

推荐 promotion ladder：

1. `control arm baseline`
2. `DAPT-only readout`
3. `DAPT + SFT`
4. `DAPT + SFT + ranking`
5. `DAPT + SFT + ranking + calibration`
6. `shadow compare`
7. `bounded canary`

未完成前一层，不应直接跳到下一层生产化。

---

## 7. Why `autoresearch` is not the current mainline

## 7.1 Comparative table

| Dimension | `base-model adaptation` | `autoresearch / self-trained small model` |
|---|---|---|
| Objective fit | 高：可直接针对 `packet triage` 任务 | 低到中：默认先优化 LM training objective |
| Data efficiency | 高 | 低 |
| Time to first useful model | 快 | 慢 |
| Rollback / deployment | 简单 | 复杂 |
| Need for large proprietary corpus | 低到中 | 高 |
| Match to current fixit evidence | 高 | 低 |
| Research upside | 中 | 高 |
| Current mainline suitability | 高 | 低 |

## 7.2 Core reason

`autoresearch` 不是没有价值，而是它更像：

- 未来研究副线
- packet-native architecture search 工具
- distillation objective/recipe search 工具

而不是 `fixit` 当前最短正确路径。

---

## 8. When it becomes worth introducing `autoresearch` as a side lane

## 8.1 Governing rule

只有当 `small base adaptation` 路线已经被充分验证，且真正出现“现成小基座 ceiling 明显”的证据，`autoresearch` 自训副线才值得进入。

## 8.2 Proposed admission gates

下列条件应至少大部分满足，才建议引入 `autoresearch` 副线：

1. `incident packet` schema 已稳定运行 `4-8 weeks`
2. multi-pilot packet 生产已连续运行，不再只是单 pilot
3. teacher/human reviewed hard cases 已积累到“有意义的千级以上”量级
4. `base-model adaptation` 已做过至少一轮 `DAPT + SFT + ranking + calibration`
5. clear evidence 显示 current small base ceiling 受限于：
   - domain-native compression
   - packet serialization inductive bias
   - ultra-cheap latency target
   - not merely data shortage
6. 已冻结：
   - latency budget
   - rollback plan
   - eval bars
   - serving target profile
7. 若要用 `autoresearch`，必须先把目标函数从 generic `val_bpb` 改为与 triage 任务一致的 objective

## 8.3 What autoresearch side lane should study then

一旦副线准入，推荐研究面应是：

- packet-native tokenizer / serialization
- tiny student architecture
- distillation objective search
- ranking-first training recipe
- latency-aware architecture search
- hardware-specific serving/training simplification

明确不建议副线先研究：

- 通用聊天能力最大化
- 无界预训练 corpus 扩张
- 与 `incident packet` 无关的 generic LM benchmark chasing

---

## 9. Recommended implementation order once admission starts

## 9.1 Near-term before implementation admission

先继续：

- daily packet accumulation
- teacher review volume growth
- human write-back completeness
- schema stability tracking
- replay breadth expansion

## 9.2 First implementation family once admitted

推荐顺序：

1. 固定 `Gemma4 teacher` 为 distillation source
2. 建 `packet_text_corpus` 与 `teacher/human supervision` 数据产物
3. 做 `small_encoder_classifier` control arm
4. 做 `Phi-3.5-mini-instruct` 的 `DAPT`
5. 做 `Phi-3.5-mini-instruct` 的 `SFT + ranking`
6. 做 calibration / threshold report
7. 和 control arm / current baseline 做 shadow compare

## 9.3 Escalation order after first implementation family

仅当 first candidate ceiling 明显时，才考虑：

- `phi-4`
- `gemma-4-E2B-it`
- 更复杂的 small reranker
- `autoresearch` packet-native side lane

---

## 10. Final recommendation

`fixit` 的 future small-model 正确主路线不是：

- 现在就用 `autoresearch` 反复试图造一个自己的小 foundation model

而是：

- 先把 `Gemma4 26B` 固定为 teacher / distillation source
- 选一个 **text-first / small / easy-to-serve** 的 base model
- 优先从 `Phi-3.5-mini-instruct` 这一类 small text model 开始
- 走 `DAPT + SFT + ranking + calibration`
- 保持 `small_encoder_classifier` 作为 control arm
- 等现成基座路线出现明确 ceiling 后，再让 `autoresearch` 进入 packet-native research side lane

一句话总结：

> `fixit` 的长期复利不在“尽快拥有自己的 small foundation model”，而在“先把 packet / teacher / outcome 数据飞轮做强，再把一个足够小、足够便宜的现成基座模型蒸馏成 student”。
