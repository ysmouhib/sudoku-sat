"""Solve sudoku puzzles with a SAT solver (PySAT)."""

from itertools import combinations
from math import isqrt


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
