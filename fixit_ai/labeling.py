from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from fixit_ai.student import LABEL_SOURCE_WEIGHTS


def build_label_ledger(training_rows: Iterable[dict], outcomes: Iterable[dict]) -> dict:
    counts_by_source: Counter[str] = Counter()
    positives_by_source: Counter[str] = Counter()
    for row in training_rows:
        source = row.get("label_source", "unknown")
        counts_by_source[source] += 1
        positives_by_source[source] += int(bool(row.get("label")))

    outcome_counts: Counter[str] = Counter(item.get("label_source", "unknown") for item in outcomes)
    outcome_severe = sum(1 for item in outcomes if item.get("actual_severe"))

    return {
        "counts_by_source": dict(counts_by_source),
        "positives_by_source": dict(positives_by_source),
        "effective_weights": LABEL_SOURCE_WEIGHTS,
        "outcome_counts_by_source": dict(outcome_counts),
        "outcome_total": sum(outcome_counts.values()),
        "outcome_severe_total": outcome_severe,
    }
