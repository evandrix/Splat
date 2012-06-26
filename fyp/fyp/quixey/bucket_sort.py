def bucketsort(arr, k):
    """
    Input:
        arr: A list of small ints
        k: Upper bound of the size of the ints in arr (not inclusive)
    Precondition:
        all(isinstance(x, int) and 0 <= x < k for x in arr)
    Output:
        The elements of arr in sorted order
    """
    counts = [0] * k
    for x in arr:
        counts[x] += 1
    sorted_arr = []
    for i, count in enumerate(counts):
        sorted_arr.extend([i] * count)
    return sorted_arr
