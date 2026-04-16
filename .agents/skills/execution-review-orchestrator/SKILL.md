---
name: execution-review-orchestrator
description: >
  用于 `fixit` 中某个 slice / family 执行后做 evidence-driven reality audit。用户说
  “执行后 review”、“对照架构和代码确认实现度”、“不确定就补最小 proof”、
  “closeout 前做 reality audit”、“看 claim 是否真的 landed”时触发；适用于
  `architecture/mvp`、schema、code、shadow report、teacher judgement、eval artifact
  之间的 claim-vs-reality 审计。
---

# Execution Review Orchestrator

## Objective

最大化当前 family 的 `claim-vs-reality alignment`。

默认目标不是写 narrative review，而是：

- 找到当前 slice 最重要的 claim
- 用 schema、code、tests、reports、sample packets、shadow evidence 去验证 claim
- 把 uncertainty 压成最小 proof
- 当前 scope 内能直接修的小缺口直接修
- 超出边界的问题转成 residual / successor handoff

## Review Order

1. 先锚定 current truth：
   - `AGENTS.md`
   - `architecture / mvp`
   - active `PLAN/STATUS/WORKSET`
2. 再看实现现实：
   - schema
   - configs
   - scripts/code
   - sample packet / report / eval artifact
3. 最后看 closeout claim 是否成立

## Classification

把发现压成三类：

- `confirmed`
- `drift`
- `uncertain`

对 `uncertain`：

- 默认补最小 proof surface
- proof 可以是 targeted test、fixture replay、sample packet、shadow snippet、report diff

## Repair Rule

- 当前 scope、当前 owner、当前验证梯子内能闭合的小缺口：直接修
- 跨 family / 跨 owner / 需要新真相面的：不要硬补，转 residual

## Preferred Evidence In This Repo

- `incident packet` example / sample
- retrieval result sample
- model score / calibration artifact
- teacher judgement sample
- shadow report
- label store snapshot
- targeted unit test / fixture replay

## Output Shape

- `findings`
- `evidence added or reused`
- `fixes landed`
- `successor residuals`
- `verdict`

可用 verdict：

- `accept`
- `accept_with_residuals`
- `blocked-closeout`
- `successor-required`
