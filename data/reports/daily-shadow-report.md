# Daily Shadow Report

- Pilot family: `crm-campaign-compile`
- Service: `g-crm-campaign`
- Replay window: `24h`

## Metrics
- severe recall: `1.0`
- top-K precision: `1.0`
- teacher escalation rate: `0.1429`
- missed severe count: `0`

## Top Severe Candidates
- `ipk_w004` `P1` `page_owner` score=0.9926 teacher=True
- `ipk_w001` `P1` `page_owner` score=0.9972 teacher=False
- `ipk_w006` `P1` `send_to_human_review` score=0.9936 teacher=False

## Rule-missed but model ranked high
- `ipk_w004` -> `P1` `page_owner`
- `ipk_w006` -> `P1` `send_to_human_review`

## Teacher Reviewed Hard Cases
- `ipk_w004` severity=4 confidence=0.74 action=page_owner

## Owner / Repo Routing Hints
- `ipk_w004` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]
- `ipk_w001` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]
- `ipk_w006` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]

## Data Freshness
- replay generated at: `2026-04-16T14:45:33Z`
- dataset count: `9`
- derived artifact count: `17`

## Fallback Usage
- live count: `0`
- fallback count: `1`

## Teacher Queue
- selected: `2`
- reviewed: `1`
- fallback: `1`
- pending: `0`
