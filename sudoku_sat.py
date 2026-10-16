"""Solve sudoku puzzles with a SAT solver (PySAT)."""

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
