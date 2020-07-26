import numpy as np


def vary_step(x: np.ndarray, s: np.ndarray):
    """
    This function takes two ndarrays of equal size and computes a third (Xnew) that has the same extremes as X,
    but with varying step, according to s

    Explanation with example:
    X = np.linspace(-10,10,100001)  # this is evenly spaced, but very fine everywhere. Bad performance
            #   y=f(X) = 1/X        =>        y' = -1/X²        step = abs(a * 1/y') = a*X²
            #   Now make X = -10.....10 with varying step as calculated above, with
            #    fine steps around 0, gross steps at the edges (-10, 10). This spares samples and improves performance
            #   Finally, recalculate y with the new X
    :param x: np.ndarray of any size, ideally consisting of an uninterupted positive sequence
    :param s: np.ndarray of
    :return Xnew:
    """
    assert x.size == s.size, 'Arrays must have the same size, by definition'
    start = x[0]
    end = x[-1]
    Xnew: list = [start]
    for i in range(1, s.size):
        a = 1/1000
        step = a * s[i]
        step = np.clip(0.1, step, 10)  # limits the step size, making it range from 0.1 to 10, for example
        Xnew.append(start+step)


    return np.array(Xnew)


if __name__ == '__main__':
    X = np.linspace(-10, 20, 31)
    # then Y is computed, and we get S from its derivative
    S = X**2
    Xnew = vary_step(x=X, s=S)
    print("X = ", X)
    print("S = ", S)
    print("Xnew = ", Xnew)
    pass
