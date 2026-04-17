# Fixit Docs

## Documents

- `docs/architecture/alert-intelligence-architecture.md` — 面向长期演进的系统架构设计稿；覆盖模块图、数据流、训练流、评测流、治理与成本控制。
- `docs/mvp/alert-intelligence-mvp.md` — 基于当前 `Prometheus + SigNoz + control-plane + bb-memory` 条件的最小可行版本落地方案。
- `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md` — 下一阶段推荐运行架构；明确数据流、两段/三段循环、哪些层现在能上、哪些层必须延后，以及每日 packet / teacher / human label 积累方法。
- `docs/architecture/fixit-small-model-strategy-memo.md` — 本地 small model 策略备忘录；冻结为什么主路线选小基座 adaptation、`Gemma4 teacher / small student` 分工、candidate order，以及 `DAPT + SFT + ranking + calibration` 训练路线。
- `docs/architecture/fixit-granite-2b-student-implementation-plan.md` — Granite 2B 当前实现方案；冻结为什么当前 implementation 选择 `Granite 2B`、接受哪些 tradeoff、如何在当前 repo 上落成 `packet render -> teacher supervision -> DAPT -> SFT -> calibration` 的第一套 local student 闭环。
- `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md` — temporal alignment / time granularity 策略稿；冻结当前 repo 哪些数据有 exact time、哪些只能继承时间、如何定义 `timestamp_quality`、为什么当前先做 `temporal lineage + episode-aware split + time-aware eval`，以及哪些 temporal experiments 可以立刻启动。
- `docs/architecture/fixit-temporal-decision-surface-admission-ladder.md` — temporal successor ladder / admission memo；冻结 P6 之后 temporal 线的终点定义、P7-P10 条件式梯子、每步 proof bar / stop condition，以及什么情况下 temporal 线并入当前 runtime、什么情况下应收束为 offline-only。
- `docs/architecture/fixit-temporal-model-sidecar-design.md` — temporal sidecar 设计稿；冻结为什么时间序列模型应作为 `temporal prior lane` 而不是新总判官、`TimesFM / Chronos family` 在 `fixit` 里的正确角色、推荐的 `packet.temporal` 扩展、数据面设计、评测指标，以及与 `Granite 2B / Gemma4 teacher` 的协同方式。

## Scope

当前文档面向一个目标：

- 把“规则引擎为主、泛化能力弱”的告警甄别体系，演进为“规则 + 检索 + 学习 + 教师模型 + 人类反馈”的分层分诊系统。

## Reading Order

1. 先读 `architecture`：确认长期正确方向与系统边界。
2. 再读 `mvp`：按最小闭环落地，不一开始追求全自动。
3. 再读 `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`：确认下一阶段默认运行面、daily accumulation 方式，以及两段/三段循环的 admission rule。
4. 再读 `docs/architecture/fixit-small-model-strategy-memo.md`：确认未来 local small model 为什么走 `small base adaptation` 主线，而不是 `autoresearch-first` 或直接把 `Gemma4 26B` 当 dense student。
5. 若当前 implementation 选择已冻结为 `Granite 2B`，再读 `docs/architecture/fixit-granite-2b-student-implementation-plan.md`：确认当前 repo 上应该如何把 Granite 2B 落成 first operational local student / floor candidate。
6. 若需要先把当前 repo 的时间锚、`timestamp_quality`、`episode-aware split`、`time-aware eval` 和 temporal lineage contract 冻结，再读 `docs/architecture/fixit-temporal-alignment-and-time-granularity-strategy.md`：确认当前该先补“时间纪律”还是先上“时间模型”，以及哪些历史实验现在就可以开跑。
7. 若需要在 P6 之后继续 temporal 方向，但不想让后续 family 失焦，先读 `docs/architecture/fixit-temporal-decision-surface-admission-ladder.md`：确认 temporal 线的终点定义、P7-P10 条件式梯子、每步 proof bar / stop condition，以及何时并入 runtime、何时收束。
8. 若需要把时间动力学能力接入 triage / ranking / teacher routing，再读 `docs/architecture/fixit-temporal-model-sidecar-design.md`：确认 `TimesFM / Chronos family` 应如何作为 `temporal sidecar` 接入，而不是取代 packet / Granite / Gemma4 的主角色。
9. 只有在上述运行面持续产出稳定证据后，再进入 local small model admission / promotion。
