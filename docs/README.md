# Fixit Docs

## Documents

- `docs/architecture/alert-intelligence-architecture.md` — 面向长期演进的系统架构设计稿；覆盖模块图、数据流、训练流、评测流、治理与成本控制。
- `docs/mvp/alert-intelligence-mvp.md` — 基于当前 `Prometheus + SigNoz + control-plane + bb-memory` 条件的最小可行版本落地方案。

## Scope

当前文档面向一个目标：

- 把“规则引擎为主、泛化能力弱”的告警甄别体系，演进为“规则 + 检索 + 学习 + 教师模型 + 人类反馈”的分层分诊系统。

## Reading Order

1. 先读 `architecture`：确认长期正确方向与系统边界。
2. 再读 `mvp`：按最小闭环落地，不一开始追求全自动。
3. MVP shadow 跑稳后，再决定是否引入本地小 LLM 作为 student 的第二阶段升级。 
