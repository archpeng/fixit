---
name: bootstrap
description: >
  用于 `fixit` 中任何非平凡任务开工前的上下文收敛。用户说“先分析项目”、
  “先确认架构边界”、“先看 observability / control-plane / memory 再动手”、
  “先收敛 incident packet / MVP truth”、“先判断应该读哪个 repo / doc / service”
  时触发；适用于实现、重构、排障、schema 设计、训练流设计、评测方案和 repo-local
  skill 设计前置分析。若任务已经明确要建立并持续推进 `plan/status/workset`，优先
  `plan-creator` 或 `execute-plan`。
---

# Bootstrap

Use this skill to avoid building against stale observability assumptions.

## Core Rule

先查 truth sources，再下判断；不要先靠 prompt 猜 repo/path/impact。

## Read First

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/architecture/alert-intelligence-architecture.md`
4. `docs/mvp/alert-intelligence-mvp.md`
5. 若任务是 skill/repo governance，再读：
   - `docs/architecture/repo-skill-migration-assessment.md`
6. 若已有 active pack，再读：
   - `docs/plan/*_PLAN.md`
   - `docs/plan/*_STATUS.md`
   - `docs/plan/*_WORKSET.md`

## Truth Order

默认按以下顺序收敛：

1. `Prometheus / SigNoz`
   - 当前异常、时间窗、log templates、trace path、service/operation 现象
2. `control-plane`
   - `service -> repo -> owner -> topology -> impact`
3. `bb-memory`
   - 相似 incident、已知误报、高危模式、owner routing 经验
4. `architecture / mvp docs`
   - intended design、MVP 边界、标签与评测口径
5. `repo code / tests / schemas / configs`
   - 最终实现真相

## Task Classes

开始前先把任务归类到以下之一：

- `incident-packet / schema`
- `candidate generation / packet builder`
- `retrieval / vector / similarity`
- `student / ranking / calibration`
- `teacher / rubric / budget gate`
- `shadow eval / label store / reporting`
- `repo-local skill / governance / docs`

## Required Output

在真正编辑前，至少明确：

- task class
- current truth sources used
- target artifact
- non-goals
- verification shape
- next handoff

## Common Handoffs

- 需要建立或重构执行包：`plan-creator`
- 已有 pack，准备按 slice 推进：`execute-plan`
- 主要产出是高密文档：全局 `dense-documentation`
- 主要是结构熵/重复真相治理：`alert-entropy-governor`
- 主要是 skill 生命周期工作：`skill-creator`

## Anti-Patterns

- 只读 docs，不查 observability / control-plane / memory
- 只看 raw logs，不收敛为 `incident packet` 语义
- 还没看 `architecture` / `mvp` 就直接定义 student/teacher 边界
- 在 repo/path/impact 未确认时直接开改

## Minimal Output Shape

- `summary`
- `truth sources checked`
- `current understanding`
- `risks / unknowns`
- `recommended handoff`
