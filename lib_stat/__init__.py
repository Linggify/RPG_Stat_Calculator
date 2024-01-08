"""Package for parsing, analyzing, simulating and plotting dice rolls
"""

from typing import Any, Callable, Dict, Self, TypeAlias, Union

import numpy

# Common Type Aliases
Distribution: TypeAlias = Dict[int, float]


# private utility methods
def _ensure_roll(roll: Any) -> 'PartialRoll':
    """Ensures that the given value is a PartialRoll. If it is an int, it is converted to a ConstantRoll. Otherwise, a TypeError is raised.

    Args:
        roll (Any): the roll to convert

    Raises:
        TypeError: if the roll is not of type int or PartialRoll

    Returns:
        PartialRoll: the roll as a PartialRoll
    """
    isInt: bool = isinstance(roll, int)
    isRoll: bool = isinstance(roll, PartialRoll)
    
    if isRoll:
        return roll
    if isInt:
        return ConstantRoll(roll)
    else:
        raise NotImplementedError(f"Cannot convert {roll} to a PartialRoll")


# classes
class PartialRoll:
    """Represents an undetermined value that is part of an ability roll. These rolls can be combined with +/- and *// to create a roll pattern.
    """
    
    # abstract methods
    def get_distribution(self) -> Distribution:
        """Returns a distribution of the possible values of this roll.
        """
        raise NotImplementedError()
    
    # implemented methods
    def simulate(self) -> int:
        """Returns a single value of this roll.
        """
        keys = []
        values = []
        for k, v in self.get_distribution().items():
            keys.append(k)
            values.append(v)

        return numpy.random.choice(keys, p=values)
    
    # operators
    def __add__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: a + b)
    
    def __radd__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: b + a)
    
    def __sub__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: a - b)
    
    def __rsub__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: b - a)
    
    def __mul__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: a * b)
    
    def __rmul__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: b * a)
    
    def __truediv__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: round(a / b))
    
    def __rtruediv__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: round(b / a))
    
    def __rfloordiv__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: b // a)
    
    def __pow__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: a ** b)
    
    def __rmod__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: b % a)
    
    def __neg__(self):
        return MergeRoll(self, ConstantRoll(0), lambda a, b: -a)
    
    def __lt__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: 1 if a < b else 0)
    
    def __le__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: 1 if a <= b else 0)
    
    def __eq__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: 1 if a == b else 0)
    
    def __ne__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: 1 if a != b else 0)
    
    def __gt__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: 1 if a > b else 0)
    
    def __ge__(self, other):
        roll = _ensure_roll(other)
        return MergeRoll(self, roll, lambda a, b: 1 if a >= b else 0)

    
class ConstantRoll(PartialRoll):
    """Represents a roll that is always a constant value.
    """
    
    def __init__(self, value: int):
        self.value = value
    
    
    # implemented methods
    def get_distribution(self) -> Distribution:
        """Returns a distribution of the possible values of this roll.
        """
        return {self.value: 1.0}
    

class MergeRoll(PartialRoll):
    """Represents a roll that is the sum of two other rolls.
    """
    
    def __init__(self, roll1: PartialRoll, roll2: PartialRoll, combiner: Callable[[int, int], int]):
        self.roll1 = roll1
        self.roll2 = roll2
        self.combiner = combiner
    
    
    # implemented methods
    def get_distribution(self) -> Distribution:
        """Returns a distribution of the possible values of this roll.
        """
        dist1 = self.roll1.get_distribution()
        dist2 = self.roll2.get_distribution()
        
        # accumulate the distributions with the combiner function
        dist = {}
        for k1, v1 in dist1.items():
            for k2, v2 in dist2.items():
                k = self.combiner(k1, k2) # combine keys with the combiner given in constructor
                v = v1 * v2
                if k in dist:
                    dist[k] += v
                else:
                    dist[k] = v
        
        return dist
    
# math utility methods
def roll_max(*rolls: Union[PartialRoll, int]) -> PartialRoll:
    """Returns a roll that is the maximum of the given rolls.

    Args:
        *rolls (PartialRoll): the rolls to take the maximum of

    Returns:
        PartialRoll: the roll that is the maximum of the given rolls
    """
    if len(rolls) == 0:
        raise ValueError("Expected at least one roll")
    
    roll = _ensure_roll(rolls[0])
    for r in rolls[1:]:
        r = _ensure_roll(r)
        roll = MergeRoll(roll, r, lambda a, b: max(a, b))
    
    return roll


def roll_min(*rolls: Union[PartialRoll, int]) -> PartialRoll:
    """Returns a roll that is the minimum of the given rolls.

    Args:
        *rolls (PartialRoll): the rolls to take the minimum of

    Returns:
        PartialRoll: the roll that is the minimum of the given rolls
    """
    if len(rolls) == 0:
        raise ValueError("Expected at least one roll")
    
    roll = _ensure_roll(rolls[0])
    for r in rolls[1:]:
        r = _ensure_roll(r)
        roll = MergeRoll(roll, r, lambda a, b: min(a, b))
    
    return roll