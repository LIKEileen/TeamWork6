import pytest
from app.services.util import merge_intervals, subtract_intervals

# --- Unit tests for merge_intervals ---

@pytest.mark.parametrize("intervals, expected", [
    # Test case 1: Empty list
    ([], []),
    # Test case 2: Single interval
    ([(1, 5)], [(1, 5)]),
    # Test case 3: Non-overlapping intervals
    ([(1, 2), (3, 4), (5, 6)], [(1, 2), (3, 4), (5, 6)]),
    # Test case 4: Overlapping intervals
    ([(1, 5), (4, 8)], [(1, 8)]),
    # Test case 5: Adjacent intervals
    ([(1, 5), (5, 8)], [(1, 8)]),
    # Test case 6: Multiple overlapping intervals
    ([(1, 4), (2, 6), (8, 10)], [(1, 6), (8, 10)]),
    # Test case 7: One interval completely contained within another
    ([(1, 10), (2, 6)], [(1, 10)]),
    # Test case 8: Unordered intervals
    ([(6, 8), (1, 9), (2, 4)], [(1, 9)]),
    # Test case 9: All intervals are the same
    ([(1, 5), (1, 5), (1, 5)], [(1, 5)]),
])
def test_merge_intervals(intervals, expected):
    """
    Tests the merge_intervals function with various scenarios.
    """
    assert merge_intervals(intervals) == expected


# --- Unit tests for subtract_intervals ---

@pytest.mark.parametrize("source, to_subtract, expected", [
    # Test case 1: Basic subtraction, no overlap
    ([(100, 200)], [(10, 50)], [(100, 200)]),
    # Test case 2: Subtracting from an empty source
    ([], [(10, 50)], []),
    # Test case 3: Subtracting an empty list
    ([(100, 200)], [], [(100, 200)]),
    # Test case 4: Subtraction that splits an interval
    ([(100, 200)], [(120, 180)], [(100, 120), (180, 200)]),
    # Test case 5: Subtraction at the beginning
    ([(100, 200)], [(80, 120)], [(120, 200)]),
    # Test case 6: Subtraction at the end
    ([(100, 200)], [(180, 220)], [(100, 180)]),
    # Test case 7: Subtraction that completely covers the source
    ([(100, 200)], [(80, 220)], []),
    # Test case 8: Source interval is completely within the subtracted interval
    ([(120, 180)], [(100, 200)], []),
    # Test case 9: Multiple subtractions from a single source interval
    ([(100, 200)], [(110, 120), (150, 160)], [(100, 110), (120, 150), (160, 200)]),
    # Test case 10: Multiple subtractions from multiple source intervals
    ([(100, 200), (300, 400)], [(150, 350)], [(100, 150), (350, 400)]),
    # Test case 11: Subtraction interval is identical to source
    ([(100, 200)], [(100, 200)], []),
])
def test_subtract_intervals(source, to_subtract, expected):
    """
    Tests the subtract_intervals function with various scenarios.
    """
    assert subtract_intervals(source, to_subtract) == expected
