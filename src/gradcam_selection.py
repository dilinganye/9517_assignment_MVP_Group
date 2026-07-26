"""Dependency-light selection of fixed prediction examples for Grad-CAM."""


def select_samples(rows, confused_pairs, correct_count, incorrect_count, pair_count, examples_per_pair):
    """Select deterministic correct, incorrect, and frequent-confusion examples."""

    selected = {}

    def add(row, reason):
        record = selected.setdefault(row["file_path"], {**row, "selection_reasons": []})
        record["selection_reasons"].append(reason)

    for row in sorted((row for row in rows if row["correct"]), key=lambda row: row["file_path"])[:correct_count]:
        add(row, "correct_example")
    for row in sorted((row for row in rows if not row["correct"]), key=lambda row: row["file_path"])[:incorrect_count]:
        add(row, "incorrect_example")
    for pair_rank, (true_label, predicted_label, _) in enumerate(confused_pairs[:pair_count], start=1):
        pair_rows = sorted(
            (
                row
                for row in rows
                if row["true_label"] == true_label and row["predicted_label"] == predicted_label
            ),
            key=lambda row: row["file_path"],
        )
        for row in pair_rows[:examples_per_pair]:
            add(row, f"confused_pair_{pair_rank}")

    if not selected:
        raise ValueError("Sample selection is empty")
    return list(selected.values())
