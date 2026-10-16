"""Solve sudoku puzzles with a SAT solver (PySAT)."""

import time
from itertools import combinations
from math import isqrt

from pysat.solvers import Solver

from puzzles import EASY_4, HARD_9, MULTI_4, TRICKY_UNSOLVABLE_4, WIKI_9


def format_grid(grid):
    """Return the grid as a printable string, with '.' for empty cells."""
    k = isqrt(len(grid))  # box size: 2 for a 4x4 grid, 3 for a 9x9 grid
    lines = []
    for r, row in enumerate(grid):
        parts = []
        for c, cell in enumerate(row):
            if c > 0 and c % k == 0:
                parts.append("|")
            parts.append(str(cell) if cell != 0 else ".")
        text = " ".join(parts)
        if r > 0 and r % k == 0:
            lines.append("".join("+" if ch == "|" else "-" for ch in text))
        lines.append(text)
    return "\n".join(lines)


def check_grid(grid: list[list[int]]) -> None:
    """Raise ValueError unless grid is an n x n grid of integers 0..n, with n = k*k."""
    n = len(grid)
    if n == 0 or isqrt(n) ** 2 != n:
        raise ValueError(f"the grid size must be a perfect square (1, 4, 9, ...), got {n}")
    for row in grid:
        if len(row) != n:
            raise ValueError(f"each row must have {n} columns, got {len(row)}")
        for value in row:
            if not isinstance(value, int) or not 0 <= value <= n:
                raise ValueError(f"cell values must be integers from 0 to {n}, got {value}")


def var(r: int, c: int, v: int, n: int) -> int:
    """Return the SAT variable meaning 'cell (r, c) contains value v'."""
    return r * n * n + c * n + v


def decode(x: int, n: int) -> tuple[int, int, int]:
    """Return the triple (r, c, v) encoded by the SAT variable x."""
    x -= 1  
    v = x % n + 1
    x //= n
    c = x % n
    r = x // n
    return r, c, v


def exactly_one(literals: list[int]) -> list[list[int]]:
    """Return clauses saying that exactly one of the literals is true."""
    clauses = [list(literals)]  # at least one of them is true
    for a, b in combinations(literals, 2):
        clauses.append([-a, -b])  # not both a and b
    return clauses


def rule_clauses(n: int) -> list[list[int]]:
    """Return the clauses expressing the sudoku rules for an n x n grid."""
    k = isqrt(n)
    values = range(1, n + 1)
    clauses = []

    # 1. Each cell contains exactly one value.
    for r in range(n):
        for c in range(n):
            clauses += exactly_one([var(r, c, v, n) for v in values])

    # 2. Each value appears exactly once in each row.
    for r in range(n):
        for v in values:
            clauses += exactly_one([var(r, c, v, n) for c in range(n)])

    # 3. Each value appears exactly once in each column.
    for c in range(n):
        for v in values:
            clauses += exactly_one([var(r, c, v, n) for r in range(n)])

    # 4. Each value appears exactly once in each box.
    for br in range(0, n, k):
        for bc in range(0, n, k):
            for v in values:
                box = [var(br + i, bc + j, v, n) for i in range(k) for j in range(k)]
                clauses += exactly_one(box)

    return clauses


def clue_clauses(grid: list[list[int]]) -> list[list[int]]:
    """Return one unit clause for each given digit of the grid."""
    n = len(grid)
    clauses = []
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                clauses.append([var(r, c, grid[r][c], n)])
    return clauses


def model_to_grid(model: list[int], n: int) -> list[list[int]]:
    """Build the grid described by a SAT model."""
    grid = [[0] * n for _ in range(n)]
    for lit in model:
        if lit > 0:
            r, c, v = decode(lit, n)
            grid[r][c] = v
    return grid


def solve(grid: list[list[int]]) -> list[list[int]] | None:
    """Return a completed copy of grid, or None if it has no solution."""
    check_grid(grid)
    n = len(grid)
    clauses = rule_clauses(n) + clue_clauses(grid)
    with Solver(name="g4", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        return model_to_grid(solver.get_model(), n)


def count_solutions(grid: list[list[int]], limit: int | None = 2) -> int:
    """Count the solutions of grid, stopping at limit (None means no limit)."""
    check_grid(grid)
    n = len(grid)
    count = 0
    clauses = rule_clauses(n) + clue_clauses(grid)
    with Solver(name="g4", bootstrap_with=clauses) as solver:
        while (limit is None or count < limit) and solver.solve():
            count += 1
            solution = model_to_grid(solver.get_model(), n)
            blocking = [-var(r, c, solution[r][c], n) for r in range(n) for c in range(n)]
            solver.add_clause(blocking)
    return count


def is_valid_solution(puzzle, solution):
    """Return True if solution is a correctly completed version of puzzle."""
    n = len(solution)
    k = isqrt(n)
    expected = set(range(1, n + 1))  # {1, 2, ..., n}

    # 1. Every row contains each value exactly once.
    for row in solution:
        if set(row) != expected:
            return False

    # 2. Every column contains each value exactly once.
    for c in range(n):
        column = [solution[r][c] for r in range(n)]
        if set(column) != expected:
            return False

    # 3. Every box contains each value exactly once.
    for br in range(0, n, k):          # top row of each box: 0, 3, 6
        for bc in range(0, n, k):      # left column of each box: 0, 3, 6
            box = [solution[br + i][bc + j] for i in range(k) for j in range(k)]
            if set(box) != expected:
                return False

    # 4. The solution agrees with every clue of the puzzle.
    for r in range(n):
        for c in range(n):
            clue = puzzle[r][c]
            if clue != 0 and solution[r][c] != clue:
                return False

    return True


def main() -> None:
    """Solve the example puzzles and print the results."""
    examples = {
        "Easy 4x4": EASY_4,
        "Wikipedia 9x9": WIKI_9,
        "Hardest 9x9": HARD_9,
        "Several solutions": MULTI_4,
        "Unsolvable": TRICKY_UNSOLVABLE_4,
    }
    for name, puzzle in examples.items():
        print(f"== {name} ==")
        print(format_grid(puzzle))
        start = time.perf_counter()
        solution = solve(puzzle)
        elapsed = time.perf_counter() - start
        if solution is None:
            print("No solution.")
        else:
            print("Solution:")
            print(format_grid(solution))
            unique = count_solutions(puzzle) == 1
            print("The solution is unique." if unique else "Several solutions exist.")
        print(f"Solved in {elapsed * 1000:.1f} ms")
        print()


if __name__ == "__main__":
    main()
