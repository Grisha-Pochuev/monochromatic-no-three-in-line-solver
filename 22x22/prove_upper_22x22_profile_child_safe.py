#!/usr/bin/env python3
"""Symmetry-safe entry point for the exact n=22 target-34 profile-child model.

The historical module ``prove_upper_22x22_profile_child.py`` combines
``row_twos <= column_twos`` with an unconditional lexicographic comparison of
the two half-boards.  Those two orientation rules can select opposite members
of a transposed pair when ``row_twos < column_twos`` and may therefore remove
both members.

This entry point deliberately disables the unconditional lexicographic rule
and keeps only the complete orientation condition
``row_twos <= column_twos``.  All line, certificate, occupancy and profile
constraints remain unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import prove_upper_22x22_profile_child as model_module


# ``build_model`` resolves this function through the module globals at runtime.
# Replacing it by a no-op removes only the unsafe second orientation rule.
def _disable_unconditional_transpose_lex(*_args, **_kwargs) -> None:
    return None


model_module.add_lex_less_or_equal = _disable_unconditional_transpose_lex


def build_model(pair_index: int, plus_twos: int, minus_twos: int):
    """Build the corrected exact model without the unsafe lexicographic cut."""
    model, points, selected, metadata = model_module.build_model(
        pair_index, plus_twos, minus_twos
    )
    metadata["transpose_symmetry_break"] = "row_twos_le_column_twos_only"
    metadata["unconditional_transpose_lex_disabled"] = True
    return model, points, selected, metadata


def solve_child(child_id: int, seconds: float, workers: int, requested_seed: int):
    """Solve one child with the corrected symmetry treatment."""
    original_build_model = model_module.build_model
    model_module.build_model = build_model
    try:
        record = model_module.solve_child(child_id, seconds, workers, requested_seed)
    finally:
        model_module.build_model = original_build_model

    record["transpose_symmetry_break"] = "row_twos_le_column_twos_only"
    record["unconditional_transpose_lex_disabled"] = True
    if record.get("proof_method") == "cp_sat_all_lines_with_certificate_profile_cuts":
        record["proof_method"] = (
            "cp_sat_all_lines_with_certificate_profile_cuts_safe_transpose_orientation"
        )
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child-id", type=int)
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--list-children", action="store_true")
    args = parser.parse_args()

    if args.list_children:
        print(json.dumps([
            {
                "child_id": child_id,
                "pair_index": model_module.decode_child(child_id)[0],
                "diag_plus_twos": model_module.decode_child(child_id)[1],
                "diag_minus_twos": model_module.decode_child(child_id)[2],
            }
            for child_id in range(model_module.child_count())
        ], indent=2))
        return

    if args.child_id is None:
        raise SystemExit("--child-id is required unless --list-children is used")

    record = solve_child(args.child_id, args.seconds, args.workers, args.seed)
    text = json.dumps(record, indent=2) + "\n"
    print(text, end="", flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    if record["status"] == "MODEL_INVALID":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
