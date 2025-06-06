"""
Some factorization methods are listed here
"""

import math
import random
from functools import reduce
from typing import Callable, Dict, List, Optional

from .common import gcd, nroot
from .primes import prime_test, primes

__all__ = ["factorize", "unfactorize"]


_PRIMES_CHECK: List[int] = primes(100)
_PRIMES_P1: List[int] = primes(100)


def rho_pollard_reduce(n: int, f: Callable[[int], int]) -> int:
    # use Pollard's (p-1) method to narrow down search
    a = random.randint(2, n - 2)
    for p in _PRIMES_P1:
        a = pow(a, p, n)

    b = a
    Q = 1
    while True:
        a = f(a)
        b = f(f(b))
        Q = (Q * (b - a)) % n

        g = gcd(Q, n)
        if g == n:
            a = b = random.randint(2, n - 2)
            Q = 1
        elif g != 1:
            return g


def _FUNC_REDUCE(n: int) -> int:
    return rho_pollard_reduce(n, lambda x: (pow(x, 2, n) + 1) % n)


def factorize(n: int) -> Dict[int, int]:
    """
    Use _FUNC_REDUCE (defaults to rho-pollard method) to factorize @n
    Return a dict like {p: e}
    """
    if n in (0, 1):
        return {n: 1}

    prime_factors: Dict[int, int] = {}

    if n < 0:
        n = -n
        prime_factors[-1] = 1

    for p in _PRIMES_CHECK:
        while n % p == 0:
            prime_factors[p] = prime_factors.get(p, 0) + 1
            n //= p

    factors: List[int] = [n]
    if n == 1:
        if not prime_factors:
            prime_factors[1] = 1
        return prime_factors

    while factors:
        n = factors.pop()

        p: Optional[int] = None
        if prime_test(n):
            p = n
            prime_factors[p] = prime_factors.get(p, 0) + 1
            continue

        is_pp = is_power(n)
        if is_pp:
            p, e = is_pp
            if prime_test(p):
                prime_factors[p] = prime_factors.get(p, 0) + e
                continue
            # else we need to factor @p and remember power
            # it's not implemented now
            # / it doesn't fasten factorize much

        divizor = _FUNC_REDUCE(n)
        other = n // divizor
        factors.append(divizor)
        if other > 1:
            factors.append(other)
    return prime_factors


def unfactorize(factors: Dict[int, int]) -> int:
    return reduce(lambda acc, p_e: acc * (p_e[0] ** p_e[1]), factors.items(), 1)


def is_power(n: int) -> Optional[tuple[int, int]]:
    limit = int(math.log(n, 2))
    for power in range(limit, 1, -1):
        p = nroot(n, power)
        if pow(p, power) == n:
            return p, power
    return None
