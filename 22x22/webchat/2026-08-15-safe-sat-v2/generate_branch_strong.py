#!/usr/bin/env python3
"""Use the safe v2 generator with an exact two-threshold line counter."""
from __future__ import annotations
import importlib.util
from pathlib import Path

base_path = Path(__file__).with_name('generate_branch.py')
spec = importlib.util.spec_from_file_location('n22_v2_base', base_path)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)


def exact_at_most_two(self, variables: list[int]) -> None:
    """Exact prefix thresholds for sum(variables) <= 2.

    old1/old2 mean that the processed prefix contains at least one/two true
    inputs.  A third true input is forbidden.  Both forward and reverse
    implications are included to give the SAT solver strong propagation.
    """
    if len(variables) <= 2:
        return
    old1 = 0
    old2 = 0
    for x in variables:
        if old2:
            self.add(-x, -old2)

        new1 = self.new()
        if old1:
            self.add(-old1, new1)
            self.add(-new1, old1, x)
        else:
            self.add(-new1, x)
        self.add(-x, new1)

        new2 = self.new()
        if old2:
            self.add(-old2, new2)
        if old1:
            self.add(-x, -old1, new2)
        # new2 -> old2 or (x and old1)
        if old2:
            self.add(-new2, old2, x)
            if old1:
                self.add(-new2, old2, old1)
            else:
                self.add(-new2, old2)
        else:
            self.add(-new2, x)
            if old1:
                self.add(-new2, old1)
            else:
                self.add(-new2)

        old1, old2 = new1, new2


base.CNF.at_most_two = exact_at_most_two

if __name__ == '__main__':
    base.main()
