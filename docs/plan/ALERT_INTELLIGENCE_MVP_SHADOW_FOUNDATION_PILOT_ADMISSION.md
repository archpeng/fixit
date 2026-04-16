# ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION_PILOT_ADMISSION

- Family: `ALERT_INTELLIGENCE_MVP_SHADOW_FOUNDATION`
- Decision: `pilot-admitted`
- Selected pilot family: `crm-campaign-compile`
- Service: `g-crm-campaign`
- Operation: `ADCService/Compile`
- Replay window: `24h`
- Decision date: 2026-04-16

---

## Why this pilot

选择 `g-crm-campaign / ADCService/Compile` 作为第一版 pilot family，原因是：

1. 单一 dominant operation，边界清楚
2. 24h 内存在真实错误：`48 / 405` calls
3. 主要错误签名稳定：`rpc error: code = 13 desc = biz error: code=500, msg=Internal server error`
4. 既能覆盖 rule-hit severe，也能覆盖 rule-missed hard case
5. 适合验证：
   - candidate generation
   - packet builder
   - retrieval similarity
   - student ranking
   - sparse teacher lane
   - shadow reporting

## Source evidence

来自 live SigNoz bounded sampling：

- `signoz_list_services(24h)` 观测到：
  - service: `g-crm-campaign`
  - numCalls: `405`
  - numErrors: `48`
  - errorRate: `11.85%`
- `signoz_get_service_top_operations(24h)`：
  - dominant operation: `ADCService/Compile`
- `signoz_search_traces(service=g-crm-campaign,error=true,24h)`：
  - repeated status message: `remote or network error: rpc error: code = 13 desc = biz error: code=500, msg=Internal server error`

## Admission boundary

本 pilot 仅用于 MVP shadow foundation 的 bounded first run：

- 不代表 production-wide rollout
- 不代表 model/generalization 已成立
- 不代表 control-plane live repo mapping 已 fully automated
- 当前允许使用 sample exports + bounded fixtures 完成 foundation 验证

## Expected output surface

围绕此 pilot family，必须能稳定产出：

- `data/samples/candidate-windows.jsonl`
- `data/samples/incident-packets.jsonl`
- `data/samples/retrieval-results.jsonl`
- `data/eval/student-scores.jsonl`
- `data/eval/teacher-judgements.jsonl`
- `data/eval/triage-decisions.jsonl`
- `data/eval/metrics-summary.json`
- `data/reports/daily-shadow-report.md`
