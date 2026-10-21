"""Sorting and searching algorithms, written by hand (no sorted() or list.index()).

merge_sort     O(n log n)  orders whole MonthResult records by one field
linear_search  O(n)        finds businesses by name or industry (unsorted data)
binary_search  O(log n)    finds a month in a history ordered by month_no
"""


def merge_sort(records, key, descending=False):
    """Return a new list of records ordered by the field named `key`.

    Whole records are moved, so every figure stays with its own month.
    Equal values keep their original order (the sort is stable).
    """
    if len(records) <= 1:
        return list(records)
    mid = len(records) // 2
    left = merge_sort(records[:mid], key, descending)
    right = merge_sort(records[mid:], key, descending)
    return _merge(left, right, key, descending)


def _merge(left, right, key, descending):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        a = getattr(left[i], key)
        b = getattr(right[j], key)
        if descending:
            take_left = a >= b
        else:
            take_left = a <= b
        if take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1
    return result


def linear_search(items, field, term):
    """Return every item whose `field` contains `term` (not case sensitive)."""
    term = term.strip().lower()
    matches = []
    for item in items:
        if term in str(getattr(item, field)).lower():
            matches.append(item)
    return matches


def binary_search(results, target_month):
    """Find one month in a list ordered by month_no. Returns None if absent."""
    low = 0
    high = len(results) - 1
    while low <= high:
        mid = (low + high) // 2
        month = results[mid].month_no
        if month == target_month:
            return results[mid]
        elif month < target_month:
            low = mid + 1
        else:
            high = mid - 1
    return None
