import math
import operator
import random
from functools import reduce
from typing import List, Optional

from .common import extract_prime_power, gcd, len_in_bits, randint_bits
from .sqrtmod import jacobi
from .strings import s2n

_primes: List[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
_small_primes_product: int = 1
_primes_bits: List[List[int]] = [[] for i in range(11)]
_primes_mask: List[bool] = []


def _init() -> None:
    global _small_primes_product, _primes, _primes_bits, _primes_mask
    _primes = primes(1024)
    for p in _primes:
        _primes_bits[len_in_bits(p)].append(p)
    _small_primes_product = reduce(operator.mul, _primes)
    _primes_mask = [(x in _primes) for x in range(_primes[-1] + 1)]
    return


def primes(until: int) -> List[int]:
    """
    Return list of primes not greater than @until. Rather slow.
    """
    global _primes, _primes_mask

    if until < 2:
        return []

    if until <= _primes[-1]:
        for index, prime in enumerate(_primes):
            if prime > until:
                return _primes[:index]

    i = _primes[-1]
    while i < until + 1:
        i += 2
        sqrt = math.sqrt(i) + 1
        for j in _primes:
            if i % j == 0:
                break
            if j > sqrt:
                _primes.append(i)
                break
    return _primes


def generate_prime(size: int, k: int = 25) -> int:
    """
    Generate a pseudo-prime with @size bits length.
    Optional arg @k=25 defines number of tests.
    """
    if size < 2:
        raise ValueError("No primes smaller than 2 bits!")

    if size <= 10:
        return random.choice(_primes_bits[size])

    while True:
        n = randint_bits(size) | 1  # only odd

        if gcd(_small_primes_product, n) != 1:
            continue

        if prime_test(n, k):
            return n
    return


def generate_prime_from_string(s: str, size: Optional[int] = None, k: int = 25) -> int:
    """
    Generate a pseudo-prime starting with @s in string representation.
    Optional arg @size defines length in bits, if is not set than +some bytes.
    Optional arg @k=25 defines number of tests.
    """
    if not size:
        if len(s) > 512:
            size = len(s) * 8 + 32
        else:
            size = len(s) * 8 + 16

    if len(s) * 8 >= size:
        raise ValueError("given size is smaller than string length")

    if size % 8:
        raise ValueError("size must be 8*n")

    extend_len = size - len(s) * 8

    visible_part = s2n(s) << extend_len
    hi = 2**extend_len

    while True:
        n = visible_part | random.randint(1, hi) | 1  # only even

        if gcd(_small_primes_product, n) != 1:
            continue

        if prime_test(n, k):
            return n
    return


def prime_test_ferma(p: int, k: int = 25) -> bool:
    """
    Test for primality based on Ferma's Little Theorem
    Totally fails in Carmichael'e numbers
    """
    if p < 2:
        return False
    if p <= 3:
        return True
    if p & 1 == 0:
        return False

    for j in range(k):
        a = random.randint(2, p - 1)
        if gcd(a, p) != 1:
            return False

        result = pow(a, p - 1, p)
        if result != 1:
            return False
    return True


def prime_test_solovay_strassen(p: int, k: int = 25) -> bool:
    """
    Test for primality by Solovai-Strassen
    Stronger than Ferma's test
    """
    if p < 2:
        return False
    if p <= 3:
        return True
    if p & 1 == 0:
        return False

    for j in range(k):
        a = random.randint(2, p - 1)
        if gcd(a, p) != 1:
            return False

        result = pow(a, (p - 1) // 2, p)
        if result not in (1, p - 1):
            return False

        if result != jacobi(a, p) % p:
            return False
    return True


def prime_test_miller_rabin(p: Optional[int], k: int = 25) -> bool:
    """
    Test for primality by Miller-Rabin
    Stronger than Solovay-Strassen's test
    """
    if p is None:
        return False
    if p < 2:
        return False
    if p <= 3:
        return True
    if p & 1 == 0:
        return False

    # p - 1 = 2**s * m
    s, m = extract_prime_power(p - 1, 2)

    for j in range(k):
        a = random.randint(2, p - 2)
        if gcd(a, p) != 1:
            return False

        b = pow(a, m, p)
        if b in (1, p - 1):
            continue

        for i in range(s):
            b = pow(b, 2, p)

            if b == 1:
                return False

            if b == p - 1:
                # is there one more squaring left to result in 1 ?
                if i < s - 1:
                    break  # good
                else:
                    return False  # bad
        else:
            # result is not 1
            return False
    return True


prime_test = prime_test_miller_rabin


_init()
