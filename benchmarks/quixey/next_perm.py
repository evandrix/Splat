import sys

def next_permutation(a):
    n = len(a)
    # Find last increasing pair
    i = n - 2
    while i >= 0 and a[i] >= a[i+1]:
        i -= 1
    if i < 0:
        #a = None  # a is decreasing, no more permutations
        return None
    else:
        # Find last number greater than a[i] (from end of list)
        # There must be one, since a[i] < a[i+1], and decreasing after
        j = n - 1
        while a[i] >= a[j]:
            j -= 1
        # and swap a[i] with a[j]
        t = a[i];  a[i] = a[j];  a[j] = t
        # Mirror the tail. Swap pairs from going from the sides to the center
        low = i + 1
        high = n - 1
        while low < high:
            # swap a[low] with a[high]
            t = a[low];  a[low] = a[high];  a[high] = t
            low += 1
            high -= 1
        return a
    return a

def next_permutation_b(perm):
    """
    Input:
        perm: A list of unique ints
    Precondition:
        perm is not sorted in reverse order
    Output:
        The lexicographically next permutation of the elements of perm
    """
    for i in range(len(perm) - 2, -1, -1):
        if perm[i] < perm[i + 1]: 
            for j in range(len(perm) - 1, i, -1):
                if perm[i] < perm[j]:
                    next_perm = list(perm)
                    next_perm[i], next_perm[j] = perm[j], perm[i]
                    next_perm[i + 1:] = reversed(next_perm[i + 1:])
                    return next_perm

if __name__ == "__main__":
    n = 3  # Just a guess
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    a = range(n) # First (increasing) permutation
    permi = 0
    while a != None:
        print "Permutation[%3d] = %s" % (permi, a)
        a = next_permutation(a)
        permi += 1
    print "Total %s Permutations" % permi
    
    assert next_permutation_b([3, 2, 4, 1]) == [3, 4, 1, 2]
