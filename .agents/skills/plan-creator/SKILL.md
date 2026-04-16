---
name: plan-creator
description: >
  用于为 `fixit` 的复杂任务创建、重构、审计可连续执行的 `plan/status/workset`
  控制面。用户说“先做计划包”、“把 MVP 拆成可连续执行 slices”、“重写 workset”、
  “让后续 session 能续跑”、“先把 incident packet / retrieval / student / teacher /
  eval 切成 bounded steps”时触发；适用于执行前建包、执行中重规划、以及 closeout
  后下一刀不清晰时的 plan refresh。
---

# Plan Creator

Use this skill to turn broad architecture intent into an executable plan pack.

## Core Promise

不要停在“写个计划”。

产出一个真正可续跑的 `PLAN/STATUS/WORKSET`，让后续 session 或 `execute-plan` 能不靠隐性上下文继续推进。

## Read First

1. `AGENTS.md`
2. `docs/architecture/alert-intelligence-architecture.md`
3. `docs/mvp/alert-intelligence-mvp.md`
4. 若已有 pack，先读当前 family 的：
   - `docs/plan/*_PLAN.md`
   - `docs/plan/*_STATUS.md`
   - `docs/plan/*_WORKSET.md`

## Good Plan Families In This Repo

优先围绕真正可闭环的工作流建 family，例如：

- `INCIDENT_PACKET_SCHEMA_FOUNDATION`
- `PACKET_BUILDER_PROM_SIG_CP_MEMORY`
- `RETRIEVAL_BASELINE_AND_SIMILARITY`
- `BASELINE_STUDENT_AND_CALIBRATION`
- `TEACHER_LANE_AND_BUDGET_GATE`
- `SHADOW_EVAL_AND_LABEL_STORE`

不要写成：

- `improve alert system`
- `make model smarter`

## Pack Rules

### `PLAN`

保持稳定，回答：

- goal
- scope
- non-goals
- phases / workstreams
- deliverables
- verification ladder
- exit criteria

### `STATUS`

保持当前真相，回答：

- current status
- active slice
- next step
- blockers
- latest evidence
- gate state

### `WORKSET`

保持执行队列，回答：

- single active slice
- owner
- expected deliverable
- verification shape
- stop condition
- residual seed

## Slice Design Heuristics

每个 slice 默认应只承载一个主意图，例如：

- 冻结 `incident packet` schema
- 完成 candidate window generator
- 完成 SigNoz evidence extraction
- 完成 control-plane enrichment
- 跑第一版 retrieval baseline
- 训练 first student baseline
- 接入 sparse teacher lane
- 产出第一版 shadow report

每个 slice 都必须写清：

- `slice_id`
- `goal`
- `target artifact`
- `verification shape`
- `stop condition`
- `next activation rule`

## When To Refresh Instead Of Continue

以下情况默认回到 `plan-creator`：

- 下一个 slice 不再清晰
- verification ladder 改了
- family scope 要扩或拆
- 当前 `WORKSET` 像 changelog，不像执行队列
- shadow 结果暴露了新的主边界问题

## Output Shape

- `refresh verdict`
- `family recommendation`
- `active slice`
- `pack structure`
- `risks / open decisions`
- `handoff to execute-plan or stop`
