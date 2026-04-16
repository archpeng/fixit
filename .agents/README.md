# fixit Agent Skills

当前目录保存 `fixit` 的 repo-local skills。

## Goal

这些 skills 只服务当前仓真正高频的主路径：

- observability-first context gathering
- `incident packet` / `retrieval` / `student` / `teacher` / `shadow eval` 的计划与执行
- claim-vs-reality audit
- severity logic / packet / memory / label drift 治理
- repo-local skill surface 维护

## Repo-Local Skills

- `bootstrap`
- `plan-creator`
- `execute-plan`
- `execution-review-orchestrator`
- `alert-entropy-governor`
- `skill-creator`
- `agents-md-curator`

## Common Chains

### 开工前

1. `bootstrap`

### 需要多步骤实现与续跑

1. `bootstrap`
2. `plan-creator`
3. `execute-plan`

### 执行后对照现实审计

1. `bootstrap`
2. `execution-review-orchestrator`

### 发现结构熵 / 逻辑重复 / packet drift

1. `bootstrap`
2. `alert-entropy-governor`

### skill 生命周期维护

1. `bootstrap`
2. `skill-creator`
3. `agents-md-curator`

## Current Truth Sources

默认顺序：

1. `Prometheus / SigNoz`
2. `control-plane`
3. `bb-memory`
4. `docs/architecture/*` + `docs/mvp/*`
5. `repo code/tests/schemas/configs`

## Validation

当前 repo 仍在早期阶段；若脚本和测试基建还未落地：

- 不要伪造“已验证”
- 优先补最小 proof surface
- 把未闭合验证明确记录到 `STATUS / WORKSET / residuals`
