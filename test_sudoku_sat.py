from pysat.solvers import Solver

from puzzles import WIKI_9, WIKI_9_SOLUTION
from sudoku_sat import decode, exactly_one, is_valid_solution, var


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


def test_var_numbers_triples_from_1_to_n_cubed():
    for n in (4, 9):
        numbers = [var(r, c, v, n) for r in range(n) for c in range(n) for v in range(1, n + 1)]
        assert sorted(numbers) == list(range(1, n**3 + 1))


def test_decode_inverts_var():
    n = 9
    for r in range(n):
        for c in range(n):
            for v in range(1, n + 1):
                assert decode(var(r, c, v, n), n) == (r, c, v)


def test_var_examples():
    assert var(0, 0, 1, 9) == 1
    assert var(1, 0, 1, 9) == 82
    assert var(8, 8, 9, 9) == 729


def test_exactly_one_clauses():
    assert exactly_one([1, 2, 3]) == [[1, 2, 3], [-1, -2], [-1, -3], [-2, -3]]


def test_exactly_one_allows_exactly_one_true_literal():
    with Solver(name="g4", bootstrap_with=exactly_one([1, 2, 3, 4])) as solver:
        models = list(solver.enum_models())
    assert len(models) == 4
    for model in models:
        assert sum(1 for lit in model if lit > 0) == 1
