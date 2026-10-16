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
