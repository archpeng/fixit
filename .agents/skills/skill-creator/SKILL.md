---
name: skill-creator
description: >
  用于 `fixit` 的 repo-local skill 生命周期管理：创建、导入、迁移、适配、替换、
  合并和轻量验证。用户说“创建 skill”、“把 workflow 变成 skill”、“把外部 skill
  迁进来并适配本项目”、“优化 trigger description”、“评估哪些 skill 该保留或删除”
  时触发；尤其适合把其他仓的 `.agents/skills/*` 改造成当前仓可用版本，并同步
  `AGENTS.md`。
---

# Skill Creator

Use this skill to keep the local skill surface small, sharp, and project-relevant.

## Core Rules

- 默认创建 repo-local skills 于 `.agents/skills/<skill-id>/`
- skill 必须服务当前仓主路径：`observability -> incident packet -> retrieval/student/teacher -> eval`
- 不要为了“看起来完整”而复制外部 skill
- skill 变更后同步：
  - `AGENTS.md`
  - `.agents/README.md`

## When Adapting Upstream Skills

先回答：

1. 源 skill 解决的是什么 workflow
2. 当前 repo 是否真的需要这个 workflow
3. 需要直接迁移，还是只保留其治理意图
4. 哪些源仓假设在当前 repo 不成立

## Minimum Checklist

- directory name 与 `name` 一致
- `description` 明确说明“做什么 + 何时触发”
- 不引用当前 repo 不存在的 scripts/docs/protocol
- 若新增或删除 skill，更新 `AGENTS.md` index
- 若结构变化，更新 `.agents/README.md`

## Preferred Output Shape

- `decision`
- `installed or changed files`
- `trigger notes`
- `follow-up sync`
- `test prompts`

## Anti-Patterns

- 直接复制别的仓技能而不改 domain truth
- 让 skill 依赖当前 repo 不存在的协议或脚本
- skill surface 过多，触发边界重叠
- 创建“万能 skill”
