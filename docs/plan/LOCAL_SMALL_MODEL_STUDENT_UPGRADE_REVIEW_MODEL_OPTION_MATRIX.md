# LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_MODEL_OPTION_MATRIX

- Family: `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW`
- Status: frozen-for-closeout
- Last verified: 2026-04-16

## Hard-case Taxonomy

- review gap count: `1`
- reviewed hard-case count: `1`
- semantic failure count: `0`
- high-rank rule-missed count: `2`
- dominant gap: `review_gap`

Readback:

- 当前 severe miss = `0`
- 当前高 novelty / rule-missed case 仍能进入高优先队列
- 当前更突出的问题是 teacher coverage / fallback，而不是 baseline model 对 severe hard case 的语义理解失败

## Option Matrix

| Option | Recommendation | Operational risk | Why |
|---|---|---:|---|
| `keep_classic_baseline` | `preferred_now` | low | bounded replay 上 `severe_recall=1.0`，当前剩余 hard case 更像 review/data gap |
| `small_encoder_classifier` | `future_candidate` | medium | 若 replay breadth 和 reviewed teacher volume 增加，可作为未来第一实施候选 |
| `small_instruct_reranker` | `defer` | high | 在当前 evidence 下先引入更复杂推理模型会增加部署与延迟复杂度 |

## Current Preferred Path

- `keep_baseline_and_accumulate_data`

解释：

- small model 路线不是被否定
- 但当前最佳动作不是 implementation，而是继续补 replay/teacher/data 基础
