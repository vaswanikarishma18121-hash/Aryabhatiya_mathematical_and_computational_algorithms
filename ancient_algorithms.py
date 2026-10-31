"""
ancient_algorithms.py
----------------------
Faithful, step-by-step Python implementations of two computational
algorithms described in Aryabhata's Aryabhatiya (499 CE):

    1. Kuttaka ("the pulveriser") - solves the linear indeterminate
       (Diophantine) equation a*x + b*y = gcd(a, b), and is used here
       to find the modular multiplicative inverse of b mod a.
       (Kak 1986; Rao & Yang 2006; Vuppala 2006)

    2. Digit-by-digit root extraction (Varga for square root, Ghana
       for cube root) - reconstructs the root of a number one digit
       at a time by grouping digits (in 2s for square root, 3s for
       cube root) from the right, exactly as described in the
       Ganitapada section of the Aryabhatiya.
       (Parakh 2007; Singh, Y.K. 2016)

Design goal
-----------
These functions deliberately do NOT call Python's built-in shortcuts
(math.isqrt, math.gcd, pow(x, -1, m)) to compute the *ancient* result.
Instead, they reproduce the original multi-step procedure and return
a full step-by-step trace, so that the authentic method is visible -
not just the final answer. Built-in functions are used ONLY to
independently *verify* correctness (see verify.py), directly
addressing Gap #4 identified in the literature review (lack of
verification against modern computational libraries).
"""

from typing import List, Tuple


# ---------------------------------------------------------------
# 1. KUTTAKA ALGORITHM  (Valli / continued-fraction method)
# ---------------------------------------------------------------
def kuttaka(a: int, b: int) -> Tuple[int, int, int, List[str]]:
    """
    Solve a*x + b*y = gcd(a, b) using Aryabhata's Kuttaka method.

    The method builds a 'Valli' (chain) of quotients by repeated
    division, exactly as described in the Aryabhatiya, and then
    back-substitutes through the chain to recover x and y.

    Returns: (gcd, x, y, steps)
    """
    steps = []
    orig_a, orig_b = a, b
    swapped = False
    if b > a:
        a, b = b, a
        swapped = True
        steps.append(f"Since {orig_b} > {orig_a}, swap so that the larger "
                     f"number is divided by the smaller: a={a}, b={b}.")

    if b == 0:
        steps.append(f"b = 0, so gcd = {a}, x = 1, y = 0 directly.")
        return a, 1, 0, steps

    # ---- Step 1: Build the Valli (chain of quotients) ----
    steps.append("STEP 1 - Build the Valli (chain of quotients) by repeated division:")
    r0, r1 = a, b
    quotients = []
    while r1 != 0:
        q = r0 // r1
        r2 = r0 % r1
        quotients.append(q)
        steps.append(f"   {r0} = {q} x {r1} + {r2}   (quotient q={q} added to Valli)")
        r0, r1 = r1, r2
    gcd = r0
    steps.append(f"   Valli (quotient chain) = {quotients}")
    steps.append(f"   gcd({a}, {b}) = {gcd}")

    # ---- Step 2: Back-substitute through the Valli ----
    steps.append("STEP 2 - Back-substitute through the Valli to recover x, y:")
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    for q in quotients:
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
        steps.append(f"   apply quotient {q}: running (x, y) = ({x0}, {y0})")
    x, y = x0, y0

    if swapped:
        x, y = y, x
        steps.append(f"   Undo the earlier swap: final (x, y) = ({x}, {y})")

    steps.append(f"RESULT: {orig_a} x ({x}) + {orig_b} x ({y}) = {gcd}")
    return gcd, x, y, steps


def kuttaka_modular_inverse(b: int, a: int) -> Tuple[int, List[str]]:
    """
    Find the modular multiplicative inverse of b mod a using the
    Kuttaka algorithm (i.e. solve b*x ~ 1 (mod a)).
    Returns (inverse, steps). Raises ValueError if gcd(a,b) != 1.
    """
    gcd, x, y, steps = kuttaka(a, b)
    if gcd != 1:
        steps.append(f"gcd({a},{b}) = {gcd} != 1, so no modular inverse exists.")
        raise ValueError(f"No modular inverse: gcd({a}, {b}) = {gcd}")
    inv = y % a
    steps.append(f"Modular inverse of {b} mod {a} = {y} mod {a} = {inv}")
    return inv, steps


# ---------------------------------------------------------------
# 2. SQUARE ROOT EXTRACTION  (Varga method)
# ---------------------------------------------------------------
def aryabhata_square_root(n: int) -> Tuple[int, int, List[str]]:
    """
    Digit-by-digit square-root extraction, grouping digits in pairs
    (Varga/non-Varga places) from the right, as described in the
    Aryabhatiya's Ganitapada.

    Returns: (integer_root, remainder, steps)
    """
    if n < 0:
        raise ValueError("Square root is not defined for negative integers here.")
    if n == 0:
        return 0, 0, ["n = 0, root = 0."]

    s = str(n)
    if len(s) % 2 != 0:
        s = '0' + s
    groups = [s[i:i + 2] for i in range(0, len(s), 2)]

    steps = [f"Group the digits of {n} in pairs from the right: {groups}"]
    root = 0
    cumulative = 0
    for g in groups:
        cumulative = cumulative * 100 + int(g)
        d = 0
        while (root * 10 + (d + 1)) ** 2 <= cumulative:
            d += 1
        steps.append(f"   bring down group '{g}' -> cumulative value = {cumulative}; "
                     f"find largest digit d such that (root*10+d)^2 <= cumulative -> d={d}")
        root = root * 10 + d
        remainder = cumulative - root ** 2
        steps.append(f"   root so far = {root}, remainder = {remainder}")
    steps.append(f"RESULT: integer square root of {n} = {root}, remainder = {remainder}")
    return root, remainder, steps


# ---------------------------------------------------------------
# 3. CUBE ROOT EXTRACTION  (Ghana / Aghana method, carry-safe)
# ---------------------------------------------------------------
def aryabhata_cube_root(n: int) -> Tuple[int, int, List[str]]:
    """
    Digit-by-digit cube-root extraction, grouping digits in triples
    (Ghana/Aghana places) from the right, as described in the
    Aryabhatiya's Ganitapada.

    NOTE ON CORRECTNESS: Singh (2016) showed that naive computer
    translations of this verse (using an incrementally-updated
    remainder via binomial expansion) can produce an incorrect digit
    when a 'carry' affects a later step. This implementation avoids
    that bug by comparing each candidate digit against the full
    cumulative value processed so far (not an approximate running
    remainder), which is guaranteed correct for any input size.
    """
    if n < 0:
        raise ValueError("Cube root is not defined for negative integers here.")
    if n == 0:
        return 0, 0, ["n = 0, root = 0."]

    s = str(n)
    pad = (-len(s)) % 3
    s = '0' * pad + s
    groups = [s[i:i + 3] for i in range(0, len(s), 3)]

    steps = [f"Group the digits of {n} in triples from the right (Ghana places): {groups}"]
    root = 0
    cumulative = 0
    for g in groups:
        cumulative = cumulative * 1000 + int(g)
        d = 0
        while (root * 10 + (d + 1)) ** 3 <= cumulative:
            d += 1
        steps.append(f"   bring down group '{g}' -> cumulative value = {cumulative}; "
                     f"find largest digit d such that (root*10+d)^3 <= cumulative -> d={d}")
        root = root * 10 + d
        remainder = cumulative - root ** 3
        steps.append(f"   root so far = {root}, remainder = {remainder}")
    steps.append(f"RESULT: integer cube root of {n} = {root}, remainder = {remainder}")
    return root, remainder, steps


if __name__ == "__main__":
    g, x, y, s = kuttaka(137, 60)
    print("\n".join(s))
