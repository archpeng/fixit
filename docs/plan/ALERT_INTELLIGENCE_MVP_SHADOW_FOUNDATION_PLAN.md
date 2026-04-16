# ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PLAN

- Status: completed
- Family: `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION`
- Created: 2026-04-16
- Plan type: repo-global execution pack
- Primary handoff: `execute-plan`
- Source anchors:
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/mvp/alert-intelligence-mvp.md`
  - `AGENTS.md`

---

## 1. Goal

在不替换现有规则系统的前提下，落出一个**可回放、可打分、可产出 shadow 报告**的 MVP foundation：

- `incident packet` v1 schema 固定
- candidate window -> packet builder 主链成立
- retrieval baseline 可返回相似事件引用
- baseline student 可做第一轮 severity/ranking 评分
- sparse teacher lane 只处理 hard cases
- shadow report / label store / eval loop 具备最小闭环

本 family 的边界是：

> 从“只有架构文档与 MVP 方案”推进到“能在一个 pilot service family 上跑通第一版 shadow foundation”。

---

## 2. Scope

## 2.1 In scope

- `schemas/`：`incident-packet.v1.json`、`teacher-judgement.v1.json`、`triage-decision.v1.json`
- `configs/`：`services.yaml`、`thresholds.yaml`、`teacher-budget.yaml`
- `scripts/`：candidate generation、packet build、retrieval、student、teacher、shadow eval 的最小骨架
- `data/samples/`、`data/eval/`、`data/reports/`：样本、评测和 shadow 产物目录
- pilot service family admission
- historical replay window selection
- baseline retrieval / student / teacher / shadow report 一阶跑通

## 2.2 Out of scope

- 本地小 LLM student 训练/部署
- production auto-action / auto-remediation
- 自动修代码或自动发布
- 全量根因分析平台化
- 多 pilot family 并行扩展
- 全量 observability UI / dashboard 产品化

---

## 3. Entry Criteria

以下事实已满足：

- `docs/architecture/alert-intelligence-architecture.md` 已定义长期架构方向
- `docs/mvp/alert-intelligence-mvp.md` 已定义 MVP 范围、顺序和成功标准
- repo 已初始化并推到远端
- `docs/plan/` 之前没有 active plan

---

## 4. Family Exit Criteria

当以下条件同时满足，当前 family 可 closeout：

1. `schemas/*.json` 已存在且字段与 MVP 文档对齐
2. 能从一个 pilot service family 的历史窗口产出：
   - `candidate-windows.jsonl`
   - `incident-packets.jsonl`
3. retrieval baseline 能对 packet 返回 top-k references / similarity metadata
4. baseline student 能输出：
   - score
   - confidence
   - novelty / or equivalent hard-case signal
5. teacher lane 已有：
   - compact payload
   - budget gate
   - trigger policy
6. shadow report 已能输出：
   - top severe candidates
   - rule missed but ranked high
   - teacher reviewed hard cases
   - owner/repo routing hints
7. 至少有一轮离线或 shadow 评测产物，能回答：
   - severe recall
   - teacher escalation rate
   - top-K precision 或同等级排序指标
8. `PLAN/STATUS/WORKSET` 已写回 closeout verdict 与 successor admission
9. `docs/plan/ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_CLOSEOUT_REVIEW.md` 已固定本 family 的 closeout evidence 与 residuals

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `WS0_FOUNDATION_FREEZE` | 冻结 schema、目录、配置与 pilot admission 前置 | `schemas/`, `configs/`, 目录骨架, pilot admission note | schema/doc 对齐，active slice closeout written |
| `WS1_PACKET_PATH` | 建立 candidate window -> packet builder 主链 | `candidate-windows.jsonl`, `incident-packets.jsonl`, builder script | 历史窗口可稳定产出 packet 样本 |
| `WS2_RETRIEVAL_BASELINE` | 提供相似事件搜索与 retrieval refs | retrieval output, similarity metadata | 至少一个 packet 能返回可解释 top-k refs |
| `WS3_STUDENT_BASELINE` | 提供第一版 student scoring / ranking / calibration | feature extractor, model artifact, threshold proposal | offline eval 可读且优于纯规则 baseline |
| `WS4_TEACHER_LANE` | 用预算受控方式接入 hard-case judge | compact payload, trigger rule, budget policy | teacher lane 只处理 hard cases 且配额清楚 |
| `WS5_SHADOW_EVAL_CLOSEOUT` | 输出 shadow report、label loop 与 family closeout | daily report, eval summary, closeout verdict | 能对外展示第一版 shadow foundation 价值 |

---

## 6. Verification Ladder

### Layer A — slice-local proof

每个 slice 至少要有一个最小证明面：

- schema/example 对齐
- config presence
- script help / smoke
- fixture replay
- sample packet / sample report readout
- metric table / eval artifact

### Layer B — workstream-close proof

当 workstream 关闭时，至少补：

- 当前 deliverables 完整性检查
- 与 `docs/mvp/alert-intelligence-mvp.md` 的字段/步骤对齐
- `STATUS/WORKSET` closeout 写回

### Layer C — family-close proof

family closeout 至少回答：

- 一个 pilot service family 是否跑通第一版 shadow foundation
- severe recall / escalation / top-K 排序证据是否已产出
- 是否具备 successor family admission 条件

---

## 7. Stop Conditions

遇到以下情况，`execute-plan` 必须停止并回 `plan-creator` 或用户：

- pilot service family 无法在当前 truth sources 下明确选定
- `incident packet` schema scope 扩大到超出 MVP 文档定义
- verification ladder 需要重写而不是补充
- retrieval / student / teacher 语义冲突，无法在当前 family 内收敛
- 当前 slice 需要引入新的 family，而不是继续当前 wave

---

## 8. Successor Admission

若本 family 完成，默认 successor 方向二选一：

1. `ALERT_INTELLIGENCE_MVP_SHADOW_HARDENING`
   - 当第一版 shadow foundation 已跑通，但需要质量、稳定性、回放规模与运维化增强
2. `LOCAL_SMALL_MODEL_STUDENT_UPGRADE`
   - 仅当 `docs/mvp/alert-intelligence-mvp.md` 第 12 节条件满足，才可进入

若 closeout 时这些 admission 条件不清晰，不得跳 family。
