import random
def shuffle(arr):
    """
    A Knuth Shuffle implementation.
    Input:
        arr: A list of unique elements
    Side Effect:
        Randomly permutes the elements of arr with uniform probability over permutations
    """
    for i in range(len(arr) - 1):
        j = random.randint(i, len(arr) - 1)
        arr[i], arr[j] = arr[j], arr[i]
