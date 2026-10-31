"""
modern_checks.py
----------------
Independent, modern ways of computing the same answers. These are used ONLY
to double-check the ancient-method results - never to produce them.
All functions work on arbitrarily large integers (no floating point).
"""
import math


def modern_inverse(b: int, a: int) -> int:
    """Modular inverse of b mod a using Python's built-in pow()."""
    return pow(b, -1, a)


def modern_sqrt(n: int) -> int:
    """Integer square root using math.isqrt()."""
    return math.isqrt(n)


def modern_cbrt(n: int) -> int:
    """Integer cube root using a plain integer binary search."""
    lo, hi = 0, 1
    while hi ** 3 <= n:
        hi *= 2
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if mid ** 3 <= n:
            lo = mid
        else:
            hi = mid
    return lo
