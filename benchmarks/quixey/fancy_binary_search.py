def find_first_in_sorted(arr, x):
    """
    Input:
        arr: A sorted list of ints
        x: A value to find
    Output:
        The lowest index i such that arr[i] == x, or -1 if x not in arr
    """
    lo = 0
    hi = len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if x == arr[mid] and (mid == 0 or x != arr[mid - 1]):
            return mid
        
        elif x <= arr[mid]:
            hi = mid
        else:
            lo = mid + 1
    return -1   # x not found in arr

if __name__ == "__main__":
    assert find_first_in_sorted([3, 4, 5, 5, 5, 5, 6], -5) == -1
    assert find_first_in_sorted([3, 4, 5, 5, 5, 5, 6], 5) == 2