# Daily Shadow Report

- Pilot family: `crm-campaign-compile`
- Service: `g-crm-campaign`
- Replay window: `24h`

## Metrics
- severe recall: `1.0`
- top-K precision: `0.6667`
- teacher escalation rate: `0.25`
- missed severe count: `0`

## Top Severe Candidates
- `ipk_w004` `P1` `page_owner` score=0.9887 teacher=True
- `ipk_w001` `P1` `page_owner` score=0.9984 teacher=False
- `ipk_w002` `P4` `observe` score=0.2992 teacher=False

## Rule-missed but model ranked high
- `ipk_w004` -> `P1` `page_owner`

## Teacher Reviewed Hard Cases
- `ipk_w004` severity=4 confidence=0.74 action=page_owner

## Owner / Repo Routing Hints
- `ipk_w004` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]
- `ipk_w001` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]
- `ipk_w002` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]
