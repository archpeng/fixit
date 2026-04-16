---
name: alert-entropy-governor
description: >
  用于治理 `fixit` 中的结构熵与重复真相：规则继续膨胀成隐式总判官、`incident packet`
  schema 漂移、raw logs 重新成为唯一输入、`bb-memory` 被误当训练主仓、`teacher rubric`
  被误当 gold truth、以及 student/retrieval/rules/teacher 各自维护一套 severity 语义。
  用户说“这套逻辑越来越乱”、“规则越补越多”、“severity 谁说了算”、“packet 和训练/线上
  不一致”、“memory/store 边界不清”、“teacher 标签该不该当真”时触发。
---

# Alert Entropy Governor

> PURPOSE: 让本仓 AI/ML/observability 系统不仅能跑，而且长期结构可维护。

## Core Outcomes

每次使用本 skill，尽量产出 4 类结论：

1. **Primary path declared**
   - 当前 canonical decision path 是什么
2. **Duplicate-truth decision**
   - 哪些 severity / routing / label 逻辑应删除，哪些应登记保留
3. **Label hierarchy clarity**
   - human outcome / production outcome / teacher / rules 各自权重是否清楚
4. **Storage-boundary verdict**
   - `bb-memory`、feature store、vector index、raw telemetry 的职责是否分开

## Required Reading

1. `AGENTS.md`
2. `docs/architecture/alert-intelligence-architecture.md`
3. `docs/mvp/alert-intelligence-mvp.md`
4. task-relevant schema / configs / code / reports

## High-Risk Drift Types In This Repo

1. `rule creep`
   - 规则继续承接越来越多本应交给 retrieval/student/teacher 的判断
2. `packet drift`
   - 在线 packet、训练样本、teacher compact packet、shadow report 字段语义不一致
3. `severity split-brain`
   - rules、student、teacher、人工处理流程各自使用不同严重性语义
4. `memory misuse`
   - 把 `bb-memory` 当训练样本仓或原始日志仓
5. `teacher over-authority`
   - 把 `teacher rubric` 直接当 gold label
6. `raw-log fallback`
   - 一遇到困难就绕过 `incident packet`，重新把原始日志洪流送进主决策路径
7. `shadow/prod drift`
   - shadow 评价口径与真实线上 action / outcome 脱钩

## Core Method

### 1. Declare the capability first

先说清这次在治理哪条能力链：

- candidate generation
- packet building
- retrieval
- student scoring
- teacher judging
- label store / eval
- shadow reporting

### 2. Declare the primary path

明确当前 canonical path：

`telemetry -> incident packet -> retrieval/student/rules -> decision mixer -> teacher(optional) -> action -> outcome`

若某段逻辑绕开主路径，必须判断：

- delete
- register as transitional
- or redesign

### 3. Apply delete-or-register

当发现重复 severity / routing / label path 时，必须二选一：

- **Delete**
  - 旧路径确实退出主链
- **Register**
  - 保留为过渡/观察/兼容路径，并写清：
    - reason
    - owner
    - removal condition

### 4. Check label hierarchy

至少明确：

- `human confirmed / production outcome` 是否高于 teacher
- `teacher` 是否只是 soft label / hard-case judge
- `rules` 是否只是 weak label / seed signal
- 当前训练权重和在线决策语义是否一致

### 5. Check storage boundaries

至少明确：

- raw telemetry 留在 observability systems
- packet/features 留在 feature store / incident store
- similarity vectors 留在 vector index
- durable operational summary 才进入 `bb-memory`

## Deliverables

默认输出：

- `capability`
- `primary path`
- `duplicate truth findings`
- `delete-or-register decisions`
- `label hierarchy verdict`
- `storage boundary verdict`
- `structural verification`

## One-Line Rule

**功能能跑不等于结构正确；只有当 `incident packet` 保持 canonical、severity 语义单一、label hierarchy 明确、memory/store 边界干净时，本仓的 alert intelligence 才算真正健康。**
