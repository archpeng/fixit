# Repo Skill Migration Assessment

- Status: draft-ssot
- Source inventory: `/home/peng/dt-git/frontend/frontend-fatboy/.agents/skills`
- Target repo: `fixit`
- Target goal: 为 `Alert Intelligence` / `incident packet` / `rules + retrieval + student + teacher + human feedback` 项目建立一组真正有复用价值的 repo-local skills

---

## 1. Project Core Need

当前 `fixit` 的核心诉求不是前端页面实现，也不是迁移收口，而是：

- 把规则引擎主导的告警甄别体系，升级为分层分诊系统
- 以 `incident packet` 作为 canonical decision unit
- 统一使用 `Prometheus + SigNoz + control-plane + bb-memory`
- 在预算受限前提下提高 severe recall
- 建立 `student / teacher / human outcome` 的持续学习闭环
- 先走 MVP：`packet -> retrieval -> baseline student -> sparse teacher -> shadow eval`

因此，repo-local skills 必须优先服务以下工作流：

1. 开工前正确收敛 truth sources
2. 把复杂任务压成可续跑的 `plan/status/workset`
3. 按 slice 执行并留证据
4. 对照架构/MVP与代码现实做 reality audit
5. 治理“新的隐式规则引擎”和重复 truth path
6. 维护本仓 AGENTS/skill surface

---

## 2. Migration Decision Matrix

| Source skill | Decision | Local target | Why |
|---|---|---|---|
| `bootstrap` | migrate | `.agents/skills/bootstrap/` | 高匹配。当前 repo 最需要 observability-first / control-plane-first / memory-aware 的上下文收敛。 |
| `plan-creator` | migrate | `.agents/skills/plan-creator/` | 高匹配。MVP 实施天然适合 `packet/schema -> retrieval -> student -> teacher -> eval` 的连续 plan pack。 |
| `execute-plan` | migrate | `.agents/skills/execute-plan/` | 高匹配。当前 repo 后续实现是典型的多阶段、可续做、证据驱动执行。 |
| `execution-review-orchestrator` | migrate | `.agents/skills/execution-review-orchestrator/` | 高匹配。需要对照 `architecture + mvp + schema + code + shadow evidence` 做 reality audit。 |
| `skill-creator` | migrate | `.agents/skills/skill-creator/` | 高匹配。当前任务本身就是 skill 迁移；后续也会继续沉淀 repo-local workflow。 |
| `agents-md-curator` | migrate | `.agents/skills/agents-md-curator/` | 中高匹配。只要本仓建立 `.agents/skills`，就需要同步维护 `AGENTS.md` 与 skill index。 |
| `code-entropy-governor` | adapt-and-rename | `.agents/skills/alert-entropy-governor/` | 核心治理意图很匹配，但风险面必须重写：本仓不是 Flutter/Rust owner drift，而是 `rule creep / duplicate severity logic / packet drift / memory misuse / teacher-label misuse`。 |
| `dense-documentation` | defer | use global skill | 全局 `dense-documentation` 已足够强；当前 repo 尚不需要单独 repo-local adapter。 |
| `feature-slice-kickoff` | defer | maybe future `pilot-slice-kickoff` | 思路有价值，但当前 repo 还没有 `docs/features/` 体系；后续若引入 pilot service / signal family pack 再适配。 |
| `repo-preflight-adapter` | defer | none for now | 依赖全局 `repo-preflight` 协议；当前 repo 用 `bootstrap` 已能覆盖主要需求。 |
| `impact-preflight-adapter` | defer | none for now | 当前 repo 还没有独立到必须拆出 impact preflight skill 的程度；先用 `bootstrap + control-plane`。 |
| `closeout-orchestrator-adapter` | reject-now | none | 当前 harness 没有对等的 closeout protocol skill；直接移植只会制造空壳。 |
| `mm-workstream-escalation-adapter` | reject-now | none | 当前 repo 没有 MM controller / subagent protocol 依赖。 |
| `flutter-style-design` | reject | none | 领域完全不匹配。 |
| `macos-preview` | reject | none | 领域完全不匹配。 |
| `vibecoding` | reject-now | use global skill if ever needed | 源 skill 偏 prototype / route shell / UI spike；当前 repo 核心不是这个。 |

---

## 3. First Migration Batch

建议当前批次只落以下 7 个：

1. `bootstrap`
2. `plan-creator`
3. `execute-plan`
4. `execution-review-orchestrator`
5. `skill-creator`
6. `agents-md-curator`
7. `alert-entropy-governor` ← 由 `code-entropy-governor` 改造而来

这样做的原因：

- 覆盖当前 repo 的真实高频工作流
- 不复制当前没有配套 protocol 的 adapter skill
- 不把前端/预览/多模型编排等外域复杂度搬进来
- 先把“开工、计划、执行、审计、治理、维护 skill surface”五件事跑顺

---

## 4. Adaptation Rules For This Repo

所有迁移 skill 都应满足以下改造规则：

### 4.1 Truth order rewrite

从 `frontend-fatboy` 的 `Flutter/Rust + control-plane + active family` 改写为：

1. `Prometheus / SigNoz` — symptom truth
2. `control-plane` — topology / repo / owner / impact truth
3. `bb-memory` — durable operational memory
4. `docs/architecture/*` + `docs/mvp/*` — design truth
5. `repo code/tests/config` — implementation truth

### 4.2 Canonical unit rewrite

把原仓的 `feature / runtime owner / migration lane` 改写为：

- `incident packet`
- `candidate window`
- `retrieval refs`
- `student score`
- `teacher judgement`
- `shadow report`

### 4.3 Guardrail rewrite

把原仓的 `owner split / compat / archive drift` 改写为：

- 不把规则系统继续长成隐式总判官
- 不让 raw logs 重新成为唯一输入主路径
- 不让 `bb-memory` 变训练主仓
- 不让 `teacher rubric` 被误当 gold truth
- 不让 student / teacher / retrieval / rules 各自维护一套 severity 语义
- 不让 `incident packet` schema 与在线决策/离线训练语义漂移

### 4.4 Closeout rewrite

当前 repo 的 closeout 默认不需要 source repo 式 graph refresh 仪式；更合理的 closeout 证据是：

- 当前 slice 产物 landed
- matching verification 已跑
- `PLAN/STATUS/WORKSET` 已更新
- 与 `architecture` / `mvp` 的 claim-vs-reality 已对照
- residual / next slice admission 已明确

---

## 5. Installed Result

本轮已选择建立 repo-local skill surface：

- `AGENTS.md`
- `.agents/README.md`
- `.agents/skills/bootstrap/SKILL.md`
- `.agents/skills/plan-creator/SKILL.md`
- `.agents/skills/execute-plan/SKILL.md`
- `.agents/skills/execution-review-orchestrator/SKILL.md`
- `.agents/skills/skill-creator/SKILL.md`
- `.agents/skills/agents-md-curator/SKILL.md`
- `.agents/skills/alert-entropy-governor/SKILL.md`

---

## 6. Future Migration Candidates

当以下条件成立时，再考虑第二批 skill：

### `pilot-slice-kickoff`

仅当 repo 出现：

- `docs/features/` 或等价的 pilot/service family packs
- 固定的 kickoff packet 模式
- 需要把某个 signal family / service family 压成 bounded slice

### `repo-preflight` / `impact-preflight`

仅当 repo 出现：

- 高频“先确认改哪里/影响面”的独立需求
- 当前 `bootstrap` 已经显著过宽
- control-plane 查询路径足够稳定

### closeout / MM adapters

仅当 repo 真的引入：

- 明确的 closeout protocol skill
- 多模型 workstream escalation 协议

否则不要为了“看起来完整”而迁移空壳技能。

---

## 7. Final Recommendation

结论很明确：

- **可直接迁移**：`bootstrap`、`plan-creator`、`execute-plan`、`execution-review-orchestrator`、`skill-creator`、`agents-md-curator`
- **可迁移但必须深改**：`code-entropy-governor -> alert-entropy-governor`
- **暂缓**：`dense-documentation`、`feature-slice-kickoff`、`repo-preflight-adapter`、`impact-preflight-adapter`
- **当前不迁移**：`closeout-orchestrator-adapter`、`mm-workstream-escalation-adapter`、`flutter-style-design`、`macos-preview`、`vibecoding`

原则不是“搬得越多越好”，而是：

> 只迁移那些能让当前 `fixit` 仓库在 observability-first、packet-first、evidence-driven 的主路径上真正变快、变稳、变清晰的技能。 
