import random
from typing import List, Optional, Tuple, Union

from .modular import invmod
from .sqrtmod import has_sqrtmod_prime_power, sqrtmod_prime_power

__all__ = ("NULL_POINT", "Curve")

Point = Tuple[Optional[int], Optional[int]]
NULL_POINT: Point = (None, None)


class Curve:
    def __init__(
        self,
        a: int,
        b: int,
        p: int,
        g: Optional[Point] = None,
        order: Optional[int] = None,
        cofactor: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.a: int = a
        self.b: int = b
        self.module: int = p

        self.g: Optional[Point] = g
        self.order: Optional[int] = order
        self.cofactor: Optional[int] = cofactor
        self.seed: Optional[int] = seed
        self.points_count: Optional[int] = None
        if self.cofactor == 1 and self.order is not None:
            self.points_count = self.order
        return None

    def is_null(self, p: Point) -> bool:
        """
        Check if a point is curve's null point
        """
        return p == NULL_POINT

    def is_opposite(self, p1: Point, p2: Point) -> bool:
        """
        Check if one point is opposite to another (p1 == -p2)
        """
        if self.is_null(p1) or self.is_null(p2):
            return False
        x1, y1 = p1
        x2, y2 = p2
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return False
        return x1 == x2 and y1 == -y2 % self.module

    def check(self, p: Point) -> bool:
        """
        Check if point is on the curve
        """
        x, y = p
        if self.is_null(p):
            return True
        if x is None or y is None:
            return False
        left = (y**2) % self.module
        right = self.right(x)
        return left == right

    def check_x(self, x: int) -> Union[bool, List[Point]]:
        """
        Check if there is a point on the curve with given @x coordinate
        """
        if x > self.module or x < 0:
            raise ValueError("Value " + str(x) + " is not in range [0; <modulus>]")
        a = self.right(x)
        n = self.module

        if not has_sqrtmod_prime_power(a, n):
            return False

        ys = sqrtmod_prime_power(a, n)
        return list(map(lambda y: (x, y), ys))

    def right(self, x: int) -> int:
        """
        Right part of the curve equation: x^3 + a*x + b (mod p)
        """
        return (x**3 + self.a * x + self.b) % self.module

    def find_points_in_range(
        self, start: int = 0, end: Optional[int] = None
    ) -> List[Point]:
        """
        List of points in given range for x coordinate
        """
        points: List[Point] = []

        if end is None:
            end = self.module - 1

        for x in range(start, end + 1):
            p = self.check_x(x)
            if p is False:
                continue
            if isinstance(p, list):
                points.extend(p)

        return points

    def find_points_rand(self, number: int = 1) -> List[Point]:
        """
        List of @number random points on the curve
        """
        points: List[Point] = []

        while len(points) < number:
            x = random.randint(0, self.module)
            p = self.check_x(x)
            if p is False:
                continue
            if isinstance(p, list):
                points.append(p[0])  # Take first point found

        return points

    def add(self, p1: Point, p2: Point) -> Point:
        """
        Sum of two points
        """
        if self.is_null(p1):
            return p2

        if self.is_null(p2):
            return p1

        if self.is_opposite(p1, p2):
            return NULL_POINT

        x1, y1 = p1
        x2, y2 = p2

        if x1 is None or y1 is None or x2 is None or y2 is None:
            return NULL_POINT

        slope = 0
        if x1 != x2:
            slope = (y2 - y1) * invmod(x2 - x1, self.module)
        else:
            slope = (3 * x1**2 + self.a) * invmod(2 * y1, self.module)

        x = (slope * slope - x1 - x2) % self.module
        y = (slope * (x1 - x) - y1) % self.module  # yes, it's that new x
        return (x, y)

    def power(self, p: Point, n: int) -> Point:
        """
        n✕P or (P + P + ... + P) n times
        """
        if n == 0 or self.is_null(p):
            return NULL_POINT

        res = NULL_POINT
        while n:
            if n & 1:
                res = self.add(res, p)
            p = self.add(p, p)
            n >>= 1
        return res

    def generate(self, n: int) -> Point:
        """
        Too lazy to give self.g to self.power
        """
        if self.g is None:
            return NULL_POINT
        return self.power(self.g, n)

    def get_order(self, p: Point, limit: Optional[int] = None) -> Optional[int]:
        """
        Tries to calculate order of @p, returns None if @limit is reached
        (SLOW method)
        """
        order = 1
        res = p
        while not self.is_null(res):
            res = self.add(res, p)
            order += 1
            if limit is not None and order >= limit:
                return None
        return order
