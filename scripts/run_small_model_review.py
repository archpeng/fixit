#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_text
from fixit_ai.small_model_review import (
    audit_phase2_conditions,
    build_deployment_review,
    build_evidence_ledger,
    build_final_verdict,
    build_guardrail_bars,
    build_hard_case_taxonomy,
    build_model_option_matrix,
    build_readiness_rubric,
    render_review_markdown,
)


def main() -> None:
    reference_date = date.today()
    rubric = build_readiness_rubric()
    evidence = build_evidence_ledger(REPO_ROOT, reference_date=reference_date)
    hard_cases = build_hard_case_taxonomy(REPO_ROOT)
    deployment = build_deployment_review(evidence)
    audit = audit_phase2_conditions(rubric, evidence, hard_cases, deployment)
    option_matrix = build_model_option_matrix(evidence, hard_cases)
    bars = build_guardrail_bars(evidence, option_matrix, deployment)
    verdict = build_final_verdict(audit, option_matrix, deployment)
    review_markdown = render_review_markdown(rubric, evidence, audit, hard_cases, option_matrix, deployment, verdict, bars)

    write_json(REPO_ROOT / "data/eval/local-small-model-readiness-rubric.json", rubric)
    write_json(REPO_ROOT / "data/eval/local-small-model-evidence-ledger.json", evidence)
    write_json(REPO_ROOT / "data/eval/local-small-model-phase2-audit.json", audit)
    write_json(REPO_ROOT / "data/eval/local-small-model-hard-case-taxonomy.json", hard_cases)
    write_json(REPO_ROOT / "data/eval/local-small-model-option-matrix.json", option_matrix)
    write_json(REPO_ROOT / "data/eval/local-small-model-deployment-review.json", deployment)
    write_json(REPO_ROOT / "data/eval/local-small-model-guardrail-bars.json", bars)
    write_json(REPO_ROOT / "data/eval/local-small-model-final-verdict.json", verdict)

    write_text(REPO_ROOT / "data/eval/local-small-model-review-readout.md", review_markdown)
    print("small model review artifacts refreshed")


if __name__ == "__main__":
    main()
