---
name: execute-plan
description: >
  用于把 `fixit` 中非平凡任务落成可续做且可持续推进的 `plan/status/workset`
  执行包，并按 bounded slice 前进。用户说“按计划推进”、“继续当前计划”、
  “建立执行包并实施”、“从 active workset 继续做”、“按 MVP 分阶段落地”时触发；
  适合 `incident packet`、retrieval、student、teacher、eval、schema、scripts、
  docs 联动的多步骤任务。若只是先理解上下文，优先 `bootstrap`；若当前 next slice
  不清晰，先回 `plan-creator`。
---

# Execute Plan

Use this skill to advance one bounded slice at a time with evidence.

## Core Promise

默认循环：

1. 读 active `PLAN/STATUS/WORKSET`
2. 找到单一 active slice
3. 落地最小产物
4. 跑 matching verification
5. 做 closeout review
6. 写回 `STATUS/WORKSET`
7. 从 residual 决定 next slice 或回 `plan-creator`

## Read First

1. `AGENTS.md`
2. relevant `architecture / mvp` docs
3. active `PLAN/STATUS/WORKSET`
4. slice 将触达的 schema / code / configs / reports

## Default Execution Rule

优先执行最小 proof-carrying slice。

如果代码/配置/数据路径还没有现成 gate：

- 不要伪造“已验证”
- 先补最小 proof surface
- 再宣称 slice landed

## Typical Slice Types In This Repo

- `docs/schema bootstrap`
- `packet builder implementation`
- `retrieval baseline`
- `student baseline`
- `teacher hard-case lane`
- `shadow report / eval loop`
- `closeout / evidence freeze`

## Verification Ladder

优先使用两层：

### Layer A — slice-local proof

例如：

- schema/example 对齐
- targeted unit test
- fixture replay
- compact sample packet readout
- single report generation smoke

### Layer B — phase-close proof

当 workstream 或 phase closeout 时，再补：

- broader replay / eval
- shadow compare readback
- metrics table / report consistency
- docs and plan surface alignment

## Closeout Protocol

每完成一个 bounded slice，至少显式回答：

- deliverable 是否 landed
- matching verification 是否跑过
- 与 `architecture / mvp` 是否一致
- 新暴露的 residual 是什么
- next slice 是否仍清楚

closeout 未写回 `STATUS/WORKSET`，默认不算真正 close。

## Escalate Back To Plan Creator When

- next slice 不明显
- 当前 family scope 已变化
- verification path 需要重设计
- residual 已经不再属于当前 wave
- 需要新 family，而不是简单 continuation

## Output Shape

- `active slice`
- `changes landed`
- `verification`
- `closeout verdict`
- `residuals`
- `next step or handoff`
