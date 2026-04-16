---
name: agents-md-curator
description: >
  用于当前仓库 `AGENTS.md` 与 `.agents/README.md` 的审计、同步和精简。用户说
  “更新 AGENTS.md”、“同步 skills 索引”、“新增/删除 skill 后补入口文档”、
  “整理 repo-level workflow / safety / invocation 规则”时触发；只处理 agent 入口文档
  与 repo-local skill surface，不处理普通业务文档。
---

# Agents Md Curator

Keep `AGENTS.md` and `.agents/README.md` accurate, concise, and aligned with the actual skill surface.

## Scope

只处理：

- `AGENTS.md`
- `.agents/README.md`
- `.agents/skills/*/SKILL.md` 与 index 的一致性

## Checklist

更新前后至少检查：

- skill 路径存在且有效
- `SKILLS_INDEX` 与目录一致
- skill 数量和列表一致
- workflow chains 仍符合当前 repo 主路径
- 没有把低频背景堆进 `AGENTS.md`

## Repo Rules

- `AGENTS.md` 只保留：宪法、truth order、workflow routing、guardrails、skill index
- `.agents/README.md` 只保留：local skills、common chains、简短 validation note
- 不把实现细节、临时脚本细节、实验记录塞进 agent 入口文档

## Preferred Output Shape

- `audit findings`
- `changes made`
- `remaining drift`
