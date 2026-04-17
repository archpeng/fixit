# Fixit Docs

## Documents

- `docs/architecture/alert-intelligence-architecture.md` — 面向长期演进的系统架构设计稿；覆盖模块图、数据流、训练流、评测流、治理与成本控制。
- `docs/mvp/alert-intelligence-mvp.md` — 基于当前 `Prometheus + SigNoz + control-plane + bb-memory` 条件的最小可行版本落地方案。
- `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md` — 下一阶段推荐运行架构；明确数据流、两段/三段循环、哪些层现在能上、哪些层必须延后，以及每日 packet / teacher / human label 积累方法。
- `docs/architecture/fixit-small-model-strategy-memo.md` — 本地 small model 策略备忘录；冻结为什么主路线选小基座 adaptation、`Gemma4 teacher / small student` 分工、candidate order，以及 `DAPT + SFT + ranking + calibration` 训练路线。

## Scope

当前文档面向一个目标：

- 把“规则引擎为主、泛化能力弱”的告警甄别体系，演进为“规则 + 检索 + 学习 + 教师模型 + 人类反馈”的分层分诊系统。

## Reading Order

1. 先读 `architecture`：确认长期正确方向与系统边界。
2. 再读 `mvp`：按最小闭环落地，不一开始追求全自动。
3. 再读 `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`：确认下一阶段默认运行面、daily accumulation 方式，以及两段/三段循环的 admission rule。
4. 再读 `docs/architecture/fixit-small-model-strategy-memo.md`：确认未来 local small model 为什么走 `small base adaptation` 主线，而不是 `autoresearch-first` 或直接把 `Gemma4 26B` 当 dense student。
5. 只有在上述运行面持续产出稳定证据后，再进入 local small model implementation family。
