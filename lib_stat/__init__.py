"""Package for parsing, analyzing, simulating and plotting dice rolls
"""

from typing import Any, Callable, Dict, List, Self, TypeAlias, TypedDict, Union
from django.test import tag

import numpy

# Common Type Aliases
class RollValue(TypedDict):
    """Represents a single value of a roll and its probability with tags
    """
    
    value: int
    """The value of the roll
    """
    
    probability: float
    """The probability of the value
    """
    
    tags: Dict[str, int]
    """The tags of the roll
    """
    

Distribution: TypeAlias = List[RollValue]
"""A distribution of the possible values of a roll
"""


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
    

def _combine_tag_dicts(tags1: Dict[str, int], tags2: Dict[str, int]) -> Dict[str, int]:
    """Combines two tag dictionaries by adding the values of the same tags. The result is a new dictionary.

    Args:
        tags1 (Dict[str, int]): the first tag dictionary
        tags2 (Dict[str, int]): the second tag dictionary

    Returns:
        Dict[str, int]: the combined tag dictionary
    """
    return {tag: tags1.get(tag, 0) + tags2.get(tag, 0) for tag in set(tags1.keys()).union(tags2.keys())}


def _equal_tag_dicts(tags1: Dict[str, int], tags2: Dict[str, int]) -> bool:
    """Checks if two tag dictionaries are equal. Two tag dictionaries are equal if they have the same tags and the same values for each tag.

    Args:
        tags1 (Dict[str, int]): the first tag dictionary
        tags2 (Dict[str, int]): the second tag dictionary

    Returns:
        bool: True if the tag dictionaries are equal, False otherwise
    """
    return all(tags1.get(tag, 0) == tags2.get(tag, 0) for tag in set(tags1.keys()).union(tags2.keys()))


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
    def simulate(self) -> RollValue:
        """Returns a single value of this roll.
        """
        values = self.get_distribution()
        args = [i for i in range(len(values))]
        probs = [v["probability"] for v in values]

        return values[numpy.random.choice(args, p=probs)]
    
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
    
    def __init__(self, value: int, *tags: str):
        self.value = value
        self.tags = tags
    
    
    # implemented methods
    def get_distribution(self) -> Distribution:
        """Returns a distribution of the possible values of this roll.
        """
        return [{ # only one roll possible, with all tags specified in the constructor
            "value": self.value,
            "probability": 1,
            "tags": {tag: 1 for tag in self.tags}
        }]
    

class DiceRoll(PartialRoll):
    """Partial Roll that simulates a fair dice
    """
    
    def __init__(self, sides: Union[int, List[int]], **tags: Union[List[int], int]):
        """Creates a new DiceRoll. A dice is defined by its sides and tags. The dice is fair, so all sides have the same probability.

        Args:
            sides (Union[int, List[int]]): the sides of the dice. If an int is given, the sides are 1 to sides. If a list is given, the sides are the elements of the list.
            **tags (Union[List[int], int]): the tags of the dice. If an int is given, the tag is assigned to just that side. If a list is given, the tag is assigned to all listed sides.
        """
        
        # if sides is an int, create a list of all sides
        self.sides = sides if isinstance(sides, list) else [i for i in range(1, sides + 1)]
        
        # if a tag is assigned an integer, make it a list with just that integer
        tag_lists = {tag: [value] if isinstance(value, int) else value for tag, value in tags.items()}
        
        self.tags_by_side: Dict[int, List[str]] = {
            side: [tag for tag, sides in tag_lists.items() if side in sides]
            for side in self.sides
        }
        
    def get_distribution(self) -> Distribution:
        return [{
            "value": side,
            "probability": 1 / len(self.sides),
            "tags": {tag: 1 for tag in self.tags_by_side[side]}
        } for side in self.sides]
    
    def __rmul__(self, other):
        if isinstance(other, int):
            roll = ConstantRoll(0)
            for _ in range(other):
                roll = MergeRoll(roll, self, lambda a, b: a + b)
                
            return roll
        
        return super().__rmul__(other)


class MergeRoll(PartialRoll):
    """Represents a roll that is the sum of two other rolls.
    """
    
    def __init__(self, roll1: PartialRoll, roll2: PartialRoll, combiner: Callable[[int, int], int]):
        """Creates a new MergeRoll. The combiner function is used to combine the values of the two rolls.

        Args:
            roll1 (PartialRoll): the first roll
            roll2 (PartialRoll): the second roll
            combiner (Callable[[int, int], int]): the combiner function. Values of the first and second roll are passed as arguments and the result is the value of this roll.
        """
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
        dist: Distribution = []
        for v1 in dist1:
            for v2 in dist2:
                k = self.combiner(v1["value"], v2["value"]) # combine values with the combiner given in constructor
                v = v1["probability"] * v2["probability"] # combine probabilities by multiplying them
                tags = _combine_tag_dicts(v1["tags"], v2["tags"]) # combine tags by adding them
                
                # try to find existing roll with equal value and tags
                existing = next((d for d in dist if d["value"] == k and _equal_tag_dicts(d["tags"], tags)), None)
                if existing is not None: # if found, add probability to existing roll value
                    existing["probability"] += v
                else: # if not found, add new roll value
                    dist.append({
                        "value": k,
                        "probability": v,
                        "tags": tags
                    })
                
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