# Exact Solutions for the Monochromatic No-Three-in-Line Problem on Checkerboard Grids

> **Latest exact result:** `D_mono(21) = 32`. The `21×21` case is closed.

This repository is part of my personal project **The Open Mathematics Project**.

The idea of this project is simple: mathematical work should be open, reusable, and readable. I want to publish configurations, scripts, certificates, notes, and partial progress under an open license, so that other people can inspect the work, reuse it, correct it, and maybe continue the search further.

This repository is devoted to the **monochromatic no-three-in-line problem on checkerboard grids**. It is a newer checkerboard-restricted version of the classical no-three-in-line problem. The aim is to approach it step by step: first by solving small and medium finite cases exactly, then by building a reusable solver and a verification archive for larger boards.

The spirit of the work is close to the old saying: water wears away stone. Not by one dramatic move, but by many small, checked, reproducible steps.

## What is the classical no-three-in-line problem?

Imagine an `n × n` square grid. We want to choose as many grid points as possible, but with one simple rule:

> No three chosen points may lie on the same straight line.

The line may have any slope. It is not enough to avoid only rows, columns, and the two main diagonal directions. A forbidden triple can appear on a shallow line, a steep line, or any other straight line passing through three grid points.

For any `n × n` grid, there is an immediate upper bound of `2n`: if we choose more than `2n` points, then some row must contain at least three chosen points. The deeper question is whether this upper bound can actually be reached, and how the best configurations behave as `n` grows.

This is why the problem is easy to state but hard to finish. It looks like a puzzle, but it leads into discrete geometry, combinatorics, computation, and the study of extremal configurations.

## What is the monochromatic checkerboard version?

Now color the grid like a chessboard.

Each grid point belongs to one of two parity classes:

```text
x + y is even
x + y is odd
```

In the monochromatic version, we are only allowed to choose points from one fixed color class.

So the rule becomes:

> Choose as many same-color grid points as possible, with no three chosen points on one straight line.

This creates a different finite problem. The board is smaller because only about half of the grid points are allowed, but the geometry is still rich. Rows, columns, diagonals, and many other slopes still matter.

We write the exact optimum as something like:

```text
D_mono(n)
```

meaning the largest number of same-color points that can be chosen on an `n × n` checkerboard grid with no three collinear.

For odd `n`, the two colors have different sizes. In that case it is useful to record both color classes separately.

## Current verified results

The repository records exact closed cases and active frontier packages separately. A case should be marked as closed only when both sides are independently checkable: a lower-bound construction and an upper-bound certificate or exhaustive search record.

| Board size | Recorded result | Status | Verification record |
|---:|---:|---|---|
| `17×17` | `D_mono(17) = 26` | closed | `17x17/` |
| `18×18` | `D_mono(18) = 27` | closed | `18x18/`, `.github/workflows/n18-search.yml` |
| `19×19` | `D_mono(19) = 29` | closed | `19x19/`, `python 19x19/verify_19x19.py` |
| `20×20` | `D_mono(20) = 30` | closed | `20x20/`, `python 20x20/verify_20x20.py`, [final exact run](https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29103139466) |
| `21×21` | `D_mono(21) = 32` | closed | `21x21/`, `python 21x21/verify_21x21.py`, [final exact run](https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29531523646) |
| `22×22` | `33 ≤ D_mono(22) ≤ 34` | active frontier | `22x22/`, [latest exact run](https://github.com/Grisha-Pochuev/monochromatic-no-three-in-line-solver/actions/runs/29815441947) |

For the `18×18` case, the repository records a verified 27-point construction and the recalculation workflow used to rule out a 28-point configuration. The relevant working package is in `18x18/`, and the GitHub Actions workflow is `.github/workflows/n18-search.yml`.

For the `19×19` case, the repository records a verified 29-point construction and a rational four-direction upper certificate proving that 30 points are impossible. Together these prove the exact value `D_mono(19) = 29`.

For the `20×20` case, the repository records a verified 30-point construction and a complete exact exclusion of every possible 31-point configuration. The final 20-branch GitHub Actions run returned 20 `INFEASIBLE` results, with zero `UNKNOWN` branches and zero solutions. Together these prove the exact value `D_mono(20) = 30`. The human-readable and machine-readable final records are stored in `20x20/runs/2026-07-10-run-29103139466/`.

For the `21×21` case, the repository records a verified rotationally symmetric 32-point construction. The four-direction integer relaxation using rows, columns, and the two diagonal families excludes 33 points for both checkerboard colors. The final GitHub Actions run returned two `INFEASIBLE` results and zero `UNKNOWN` results. Together these prove `D_mono(21) = 32`. The final records are stored in `21x21/runs/2026-07-16-run-29531523646/`.

For the `22×22` case, the repository records a verified 33-point construction and an exact all-lines exclusion search for a possible 34th point. Run `29815441947` processed the complete 56-child frontier, strictly excluded 46 more children, and left 10 exact children unresolved. In total 2630 of all 2640 children are now closed; therefore the certified status remains `33 ≤ D_mono(22) ≤ 34`.

## A small example

On a normal chessboard-style grid, the problem is not just about avoiding three points in a row.

Three selected points are also forbidden if they lie on a long diagonal, a short diagonal, or a slanted line of slope `2/1`, `3/2`, `5/3`, and so on.

This is the main source of difficulty. A configuration can look safe locally but fail because of one hidden long line crossing the board.

The checkerboard restriction makes the problem visually simple but mathematically sharp: we are trying to place many same-color points while avoiding every possible straight-line accident.

## Short history

The classical no-three-in-line problem is usually attributed to the British puzzle maker **Henry Ernest Dudeney**. It began as a recreational mathematics puzzle about placing pawns on a chessboard-like grid so that no three of them lie in a straight line.

Later the problem became part of serious discrete geometry. It was studied by many mathematicians through explicit constructions, upper bounds, probabilistic arguments, computational searches, and related versions on finite and infinite grids.

Important names connected with the classical problem include:

- **Henry Ernest Dudeney**, who popularized the original puzzle form.
- **Paul Erdős**, who pointed out a simple algebraic construction using points of the form `(x, x²)` modulo a prime.
- **Richard K. Guy** and **Patrick A. Kelly**, whose 1968 paper is one of the classical references for the problem.
- **Achim Flammenkamp**, who carried out important computational work on exact and near-exact configurations.
- **Peter Brass**, **William Moser**, and **János Pach**, who discussed the problem in the broader setting of lattice-point problems in discrete geometry.
- **Thomas Prellberg**, who has worked on the classical problem and introduced the checkerboard-restricted monochromatic version studied here.

So the problem has two lives at the same time. It is simple enough to explain as a puzzle, but it also belongs to a long mathematical tradition.

## Why this problem matters

This problem is interesting for several reasons.

- It is a bridge between recreational mathematics and research mathematics.
- It is simple enough to explain without technical language.
- It produces hard finite search problems.
- It connects geometry, number theory, combinatorics, and algorithms.
- It is a good test case for computer-assisted mathematical exploration.
- It is a natural playground for hybrid work: human ideas, exact solvers, search scripts, and independently checkable certificates.
- It has links to graph drawing, computational geometry, and the control of unwanted collinearities in point configurations.

The monochromatic checkerboard version is especially suitable for step-by-step exact work. It has a clean visual formulation, but it also admits strong linear-programming upper bounds using rows, columns, and the two diagonal families of slopes `+1` and `-1`.

This makes it a good test case for a modern style of open mathematical work: not only finding configurations, but also recording certificates that prove optimality.

## How the verification works

The verification is meant to be simple and reproducible.

A checking script should verify:

1. the listed points lie on the correct board;
2. all listed points belong to the required checkerboard color class;
3. the points are distinct;
4. no three selected points are collinear;
5. the claimed lower-bound configuration has the stated size;
6. the upper-bound certificate or exhaustive search record excludes configurations of the next size.

The important point is that the proof should not depend on trust in a search program alone.

The search program may find the configuration, but the final result should be checked by a smaller independent verification script or by a reproducible search/certificate record.

## What this repository is trying to do

This repository is not meant to be only a one-case archive for the `17 × 17`, `18 × 18`, `19 × 19`, `20 × 20`, or `21 × 21` boards.

The long-term goal is to build a step-by-step exact solver and verification archive for the monochromatic no-three-in-line problem on checkerboard grids.

The plan is to collect:

- exact values for increasing board sizes;
- optimal configurations;
- lower-bound search scripts;
- upper-bound certificates;
- independent verification scripts;
- notes about failed approaches;
- records of useful reductions and symmetries;
- readable explanations of how each result was found.

Some parts may be computational. Some parts may be mathematical notes. Some parts may be failed attempts that are still useful because they show what does not work.

The long-term aim is to make the search process transparent: not only to store final configurations, but also to show how they were found, checked, improved, or rejected.

## Project philosophy

This repository follows the spirit of **The Open Mathematics Project**:

- open notes,
- open license,
- reproducible steps,
- reusable results,
- clear intermediate records,
- honest records of dead ends,
- gradual progress instead of hidden final answers.

The point is not only to solve instances, but also to make the process visible.

If something here helps another person move the problem even a little further, then the repository has already done part of its job.

The exact structure can change as the project grows. The main principle is simple: every result should have a readable explanation and a reproducible check.

## Further reading

- Thomas Prellberg, **No-three-in-line sets on the checkerboard grid**  
  https://arxiv.org/abs/2605.09215

- Thomas Prellberg, **Constraint Satisfaction Programming for the No-three-in-line Problem**  
  https://arxiv.org/abs/2602.07751

- Richard K. Guy and Patrick A. Kelly, **The No-Three-In-Line Problem**  
  https://www.cambridge.org/core/journals/canadian-mathematical-bulletin/article/nothreeinline-problem/B126DA7E4957722BAC70AC7B7F6E1FA2

- Achim Flammenkamp, **The No-Three-In-Line Problem**  
  https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html

- Wolfram MathWorld, **No-Three-in-a-Line Problem**  
  https://mathworld.wolfram.com/No-Three-in-a-Line-Problem.html

- Wikipedia, **No-three-in-line problem**  
  https://en.wikipedia.org/wiki/No-three-in-line_problem

## About

**The Open Mathematics Project:** step-by-step exact solver and verification archive for the monochromatic no-three-in-line problem on checkerboard grids.
