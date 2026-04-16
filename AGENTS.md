# AGENTS.md

## Project Role

- 本仓库是 `fixit`：用于建设 `Alert Intelligence` / `incident triage` / `severity ranking` / `escalation routing` 系统。
- 当前主目标不是自动修复代码，也不是 observability UI，而是把“规则引擎主导、泛化能力弱”的告警甄别体系，升级为：
  - `rules + retrieval + student + teacher + human feedback`
- 当前第一阶段主路径是 `MVP shadow system`，不是 production auto-action。

## Core Constitution

- canonical decision unit 固定为：`incident packet`
- 当前长期正确方向遵循 `The Bitter Lesson`：优先投入 `search + learning + feedback + compute-aware cascade`，而不是 endless heuristics
- `rules` 保留为高精度 hard signal / seed signal，不再独占最终严重性判决
- `student` 负责 bulk triage / ranking / confidence
- `teacher` 只负责高价值 hard cases，不做全量原始日志扫描
- `human outcome` / production outcome 的标签优先级高于 `teacher rubric`
- `bb-memory` 是 durable operational memory，不是全量训练主仓
- `feature store / incident store / vector index` 与 `bb-memory` 的职责必须分开
- 禁止把 prompt engineering 继续堆成新的隐式规则引擎

## Truth Order

本仓默认按以下顺序取证：

1. `Prometheus / SigNoz`
   - 指标、日志、trace、异常时间窗、error templates、top operations
2. `control-plane`
   - service / repo / owner / topology / blast radius / path routing truth
3. `bb-memory`
   - 历史 incident、已知误报、高危模式、owner routing 经验
4. `docs/architecture/*` + `docs/mvp/*`
   - 设计真相、MVP 边界、标签策略、评测口径
5. `repo code / tests / schemas / configs`
   - 最终实现真相

若问题属于“观察到什么、影响谁、该看哪个 repo/service/doc”，默认不要直接猜，先查 truth sources。

## Repo Skills

canonical repo-local skills path:

`.agents/skills/`

当前 repo-local skills：

- `bootstrap`
- `plan-creator`
- `execute-plan`
- `execution-review-orchestrator`
- `alert-entropy-governor`
- `skill-creator`
- `agents-md-curator`

## SKILLS_INDEX

- [agents-md-curator](.agents/skills/agents-md-curator/SKILL.md) — 维护 `AGENTS.md`、`.agents/README.md` 与 repo-local skill index 的一致性。
- [alert-entropy-governor](.agents/skills/alert-entropy-governor/SKILL.md) — 治理 `rule creep`、duplicate severity logic、packet drift、memory misuse 与 label hierarchy drift。
- [bootstrap](.agents/skills/bootstrap/SKILL.md) — 非平凡任务开工前先收敛 observability truth、control-plane 路由、memory 与架构边界。
- [execute-plan](.agents/skills/execute-plan/SKILL.md) — 把多步骤任务落成 `plan/status/workset` 执行包并按 slice 持续推进。
- [execution-review-orchestrator](.agents/skills/execution-review-orchestrator/SKILL.md) — 在执行后对照 `architecture/mvp`、schema、代码、shadow evidence 做 reality audit。
- [plan-creator](.agents/skills/plan-creator/SKILL.md) — 为 `incident packet / retrieval / student / teacher / eval` 等复杂任务设计或修复可连续执行的 plan pack。
- [skill-creator](.agents/skills/skill-creator/SKILL.md) — 创建、导入、改造本仓 repo-local skills，并同步 `AGENTS.md`。

## Workflow Constraints

1. 非平凡任务默认先走 `bootstrap`。
2. 如果任务需要多步推进、断点恢复、阶段 closeout，先走 `plan-creator`，再进入 `execute-plan`。
3. 如果实现后要判断“文档说的是否真的 landed”，走 `execution-review-orchestrator`。
4. 如果问题本质是 severity 逻辑重复、rule creep、packet/schema drift、teacher/memory/store 边界混乱，走 `alert-entropy-governor`。
5. 新建或迁移 skill 时，走 `skill-creator -> agents-md-curator`。
6. 如果 control-plane / observability / memory 都还没看，就不要直接给出 repo/path/impact 结论。

## Skill Layering

本仓采用：

- global skills：通用 planning / documentation / audit / repo design 能力
- repo-local skills：把全局能力收紧到当前 `Alert Intelligence` 主路径

典型链路：

- 开工前收敛：`bootstrap`
- 建 plan 后执行：`bootstrap -> plan-creator -> execute-plan`
- 执行后 reality audit：`bootstrap -> execution-review-orchestrator`
- skill 生命周期：`bootstrap -> skill-creator -> agents-md-curator`
- 结构治理：`bootstrap -> alert-entropy-governor`

## Current SSOT

默认先读：

- `docs/README.md`
- `docs/architecture/alert-intelligence-architecture.md`
- `docs/mvp/alert-intelligence-mvp.md`
- `docs/architecture/repo-skill-migration-assessment.md`（仅当任务是 skill surface / repo governance）

如果已有活跃执行包，再读：

- `docs/plan/*_PLAN.md`
- `docs/plan/*_STATUS.md`
- `docs/plan/*_WORKSET.md`

## Documentation Conventions

- 新增文档默认简体中文；稳定英文关键词保持原样：`incident packet`、`teacher rubric`、`shadow mode`、`feature store`、`vector index` 等
- 优先高密度、执行导向写法：decision list、table、schema、field list、verification ladder
- `architecture` 负责长期设计真相
- `mvp` 负责阶段性落地方案
- `plan` 负责当前执行控制面
- `schemas/configs/scripts/data` 负责运行面，而不是 narrative docs

## Guardrails

- 不把 raw logs 直接当成唯一训练/判断主路径；优先压成 `incident packet`
- 不让 `rules`、`retrieval`、`student`、`teacher` 各自维持一套互不对齐的 severity 语义
- 不让 `bb-memory` 充当海量 packet / raw log 仓库
- 不在没有真实 outcome 的情况下，把 `teacher` 当成最终真相
- 不在没有 shadow / eval evidence 的情况下宣称模型升级成立
- 不因为“先能跑”就长期保留 prompt-only 或 notebook-only 的隐式主路径

## Verification Routing

- docs / skills 变更：检查路径、索引、cross-reference 与术语一致性
- schema 变更：检查 schema、example、MVP deliverable 对齐
- pipeline / model 变更：优先跑最小 targeted test、fixture replay 或 shadow compare
- phase closeout：要求写回 `PLAN/STATUS/WORKSET`，并记录 evidence / residual / next slice admission

## Invocation Notes

- 当前核心架构 SSOT：`docs/architecture/alert-intelligence-architecture.md`
- 当前 MVP 方案：`docs/mvp/alert-intelligence-mvp.md`
- 当前 skills 迁移评估：`docs/architecture/repo-skill-migration-assessment.md`
- 当前 repo 远端：`https://github.com/archpeng/fixit.git`
