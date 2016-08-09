import math


def binomial_expression(x, y):
    """
    A math function to calculate the nCr.
    @param n: the n value
    @param r: the r value
    @return: nCr
    """
    try:
        binom = math.factorial(x) // math.factorial(y) // math.factorial(x - y)
    except ValueError:
        binom = 0
    return binom
