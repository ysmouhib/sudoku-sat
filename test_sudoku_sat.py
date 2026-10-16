from puzzles import WIKI_9, WIKI_9_SOLUTION
from sudoku_sat import is_valid_solution


def test_known_solution_is_valid():
    assert is_valid_solution(WIKI_9, WIKI_9_SOLUTION)


def test_swapping_two_cells_breaks_the_solution():
    bad = [row[:] for row in WIKI_9_SOLUTION]  # copy every row
    bad[0][0], bad[0][1] = bad[0][1], bad[0][0]
    assert not is_valid_solution(WIKI_9, bad)


def test_valid_grid_that_ignores_the_clues_is_rejected():
    swap = {1: 2, 2: 1}
    other = [[swap.get(v, v) for v in row] for row in WIKI_9_SOLUTION]
    assert not is_valid_solution(WIKI_9, other)
