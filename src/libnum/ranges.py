import json
from functools import reduce
from typing import Any, Iterator, List, Tuple

"""
TODO: fix properties for empty
or not? IndexError is ok
max([]) = ValueError
"""


class Ranges(object):
    """
    Represent Int-ranges unions
    Example: 3-10 or 15-30 or 31-31
    - operators:
        intersection ( & )
        union ( | )
    - iterator yields all integers from ranges
    - .segments property - tuple of segments
        - len(R.segments) - count of segments
        - iter(R.segments) - iterator for segments
        - etc.
    - add_range method - unite with (x, y) range
    """

    def __init__(self, *ranges: Tuple[int, int]):
        self._segments: List[Tuple[int, int]] = []
        for a, b in ranges:
            self.add_range(a, b)

    def add_range(self, x: int, y: int) -> None:
        if y < x:
            raise ValueError("end is smaller than start: %d < %d" % (y, x))

        for index, (a, b) in enumerate(self._segments):
            if y < a - 1:
                self._segments.insert(index, (x, y))
                return

            if x > b + 1:
                continue

            new_a = min(a, x)
            new_b = max(b, y)

            index2 = index + 1
            while index2 < len(self._segments):
                a, b = self._segments[index2]
                if new_b < a - 1:
                    break

                new_b = max(new_b, b)
                del self._segments[index2]

            self._segments[index] = (new_a, new_b)
            return
        self._segments.append((x, y))
        return

    def __or__(self, other: "Ranges") -> "Ranges":
        res = Ranges()
        for x, y in self._segments:
            res.add_range(x, y)
        for x, y in other._segments:
            res.add_range(x, y)
        return res

    def __and__(self, other: "Ranges") -> "Ranges":
        res = []
        index1 = 0
        index2 = 0
        list1 = self._segments
        list2 = other._segments
        while index1 < len(list1) and index2 < len(list2):
            a, b = list1[index1]
            A, B = list2[index2]

            if A < a:
                list2, list1 = list1, list2
                index2, index1 = index1, index2
                a, b, A, B = A, B, a, b

            # a..A..B..b
            if a <= A <= B <= b:
                res.append((A, B))
                index2 += 1
                continue

            # a..b...A..B
            if b < A:
                index1 += 1
                continue

            # a..A..b..B
            res.append((A, b))
            index1 += 1
        return Ranges(*res)

    def __iter__(self) -> Iterator[int]:
        for a, b in self._segments:
            while a <= b:
                yield a
                a += 1
        return

    def __eq__(self, other: Any) -> bool:
        return self.segments == other.segments

    @property
    def len(self) -> int:
        return reduce(lambda acc, ab: acc + 1 + ab[1] - ab[0], self._segments, 0)

    @property
    def min(self) -> int:
        return self._segments[0][0]

    @property
    def max(self) -> int:
        return self._segments[-1][1]

    @property
    def segments(self) -> Tuple[Tuple[int, int], ...]:
        return tuple(self._segments)

    def __str__(self) -> str:
        return str(self.segments)

    def __contains__(self, other: int) -> bool:
        assert isinstance(other, int)
        for a, b in self._segments:
            if a <= other <= b:
                return True
        return False

    def to_json(self) -> str:
        return json.dumps(self._segments)

    @classmethod
    def from_json(cls, j: str) -> "Ranges":
        return Ranges(*json.loads(j))
