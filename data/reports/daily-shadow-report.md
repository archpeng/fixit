# Daily Shadow Report

- Pilot family: `crm-campaign-compile`
- Service: `g-crm-campaign`
- Replay window: `24h`

## Metrics
- severe recall: `1.0`
- top-K precision: `1.0`
- teacher escalation rate: `0.7`
- missed severe count: `0`

## Top Severe Candidates
- `ipk_w004` `P1` `page_owner` score=0.9808 teacher=True
- `ipk_w006` `P1` `page_owner` score=0.983 teacher=True
- `ipk_w001` `P1` `page_owner` score=0.9927 teacher=False

## Rule-missed but model ranked high
- `ipk_w004` -> `P1` `page_owner`
- `ipk_w006` -> `P1` `page_owner`

## Teacher Reviewed Hard Cases
- `ipk_w002` severity=2 confidence=0.61 action=create_ticket
- `ipk_w004` severity=4 confidence=0.74 action=page_owner
- `ipk_w006` severity=4 confidence=0.69 action=page_owner
- `ipk_w007` severity=2 confidence=0.58 action=create_ticket
- `ipk_w010` severity=2 confidence=0.56 action=create_ticket
- `ipk_w011` severity=2 confidence=0.59 action=create_ticket
- `ipk_w012` severity=2 confidence=0.55 action=create_ticket

## Owner / Repo Routing Hints
- `ipk_w004` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]
- `ipk_w006` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]
- `ipk_w001` owner=`growth-campaign-oncall` repos=[g-crm-campaign, ad-compiler] similar=[INC-1422, INC-1198]

## Data Freshness
- replay generated at: `2026-04-17T01:56:35Z`
- dataset count: `9`
- derived artifact count: `17`

## Fallback Usage
- live count: `0`
- fallback count: `2`

## Teacher Queue
- selected: `7`
- reviewed: `7`
- fallback: `0`
- pending: `0`
