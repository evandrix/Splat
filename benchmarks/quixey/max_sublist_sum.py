def max_sublist_sum(arr):
    """
    Efficient equivalent to max(sum(arr[i:j]) for 0 <= i <= j <= len(arr))
    Algorithm source: WordAligned.org by Thomas Guest
    Input:
        arr: A list of ints
    Output:
        The maximum sublist sum
    """
    max_ending_here = 0
    max_so_far = 0
    for x in arr:
        max_ending_here = max(0, max_ending_here + x)
        max_so_far = max(max_so_far, max_ending_here)
    return max_so_far

if __name__ == "__main__":
    assert max_sublist_sum([4, -5, 2, 1, -1, 3]) == 5
