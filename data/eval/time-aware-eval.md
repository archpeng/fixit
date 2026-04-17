# Time-aware Historical Eval

## Summary
- episode count: `4`
- packet count: `10`
- severe recall: `1.0`
- top-K precision: `1.0`
- teacher escalation rate: `0.0`
- severe episode recall: `1.0`
- top-K episode precision: `0.3333`

## Cutoff Leakage Audit
- folds with relaxed history > strict: `4`
- folds with relaxed refs > strict: `4`
- max history incident gap: `4`

## Folds
- `ep_inc-compile-500` packets=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] train_rows=6 strict_history=0 relaxed_history=4
- `ep_inc-compile-warmup` packets=['ipk_w002', 'ipk_w007'] train_rows=6 strict_history=0 relaxed_history=4
- `ep_inc-queue-depth` packets=['ipk_w005'] train_rows=8 strict_history=0 relaxed_history=4
- `ep_inc-other-service` packets=['ipk_w010', 'ipk_w011', 'ipk_w012'] train_rows=12 strict_history=2 relaxed_history=4
