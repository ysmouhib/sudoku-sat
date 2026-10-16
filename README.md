# Sudoku SAT solver

Solves sudoku puzzles by encoding them as a SAT problem and calling a SAT
solver through [PySAT](https://pysathq.github.io). It works for any size
n = k² (4×4, 9×9, 16×16, …), reports puzzles that have no solution, and can
check whether a solution is unique.

## Installation

Requires Python 3.10–3.14.

```
python -m venv .venv
.venv\Scripts\activate          # on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Solve the example puzzles from `puzzles.py`:

```
python sudoku_sat.py
```

Or from Python, with a grid given as a list of lists (0 = empty cell):

```python
from puzzles import WIKI_9
from sudoku_sat import count_solutions, format_grid, solve

print(format_grid(solve(WIKI_9)))
print(count_solutions(WIKI_9))   # 1: the solution is unique
```

`solve` returns the completed grid, or `None` if the puzzle has no solution.

## How it works

**Variables.** For each cell (r, c) and value v, a boolean variable x(r, c, v)
means "cell (r, c) contains v". They are numbered
var(r, c, v) = r·n² + c·n + v, a bijection onto 1…n³ (729 variables for 9×9).

**Rules.** A completed grid is valid when exactly one variable is true in each
of these 4n² groups:

1. each cell contains exactly one value;
2. each value appears exactly once in each row;
3. each value appears exactly once in each column;
4. each value appears exactly once in each box.

"Exactly one of l₁…lₘ" becomes one clause (l₁ ∨ … ∨ lₘ) plus one clause
(¬lᵢ ∨ ¬lⱼ) per pair i < j. For a 9×9 grid that gives 324 × 37 = 11,988
clauses.

**Clues.** Each given digit becomes a one-literal clause.

**Decoding.** The true variables of the solver's model give the value of each
cell.

**Uniqueness.** After finding a solution S, the clause "at least one cell
differs from S" is added and the solver is called again: if no new solution
exists, S was unique.

## Tests

```
python -m pytest
```

The tests check each building block separately. Notable ones:

- every solution found by SAT is verified by an independent checker that
  does not use SAT;
- the rules alone have exactly 288 models for 4×4, the known number of
  complete 4×4 sudoku grids;
- unsolvable and malformed puzzles are handled.

## Project structure

- `sudoku_sat.py`: encoding, solving, checking and printing
- `puzzles.py`: example puzzles
- `test_sudoku_sat.py`: tests
