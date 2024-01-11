"""Default Combinerfuncions for rolls
"""

from functools import reduce
from math import comb
from typing import Dict

from .roll_types import RollValue, VarargsCallable

# Tag Combiners

def tag_combiner_additive(*tags: Dict[str, int]) -> Dict[str, int]:
    """Combines the given tags by adding their values

    Args:
        *tags (Dict[str, int]): the tags to combine

    Returns:
        Dict[str, int]: the combined tags
    """
    return {tag: sum([t.get(tag, 0) for t in tags]) for tag in reduce(lambda a, b: a.union(b), [set(t.keys()) for t in tags], set())}


# Combiner Factories

def combiner_from_value_and_tag_combiner(v_combiner: VarargsCallable[RollValue, int], tag_combiner: VarargsCallable[RollValue, Dict[str, int]]) -> VarargsCallable[RollValue, RollValue]:
    """Creates a combiner function from a value combiner and a tag combiner

    Args:
        v_combiner (VarargsCallable[RollValue, RollValue]): the value combiner
        tag_combiner (VarargsCallable[Dict[str, int], Dict[str, int]]): the tag combiner

    Returns:
        VarargsCallable[RollValue, RollValue]: the combiner function
    """
    def combiner(*rolls: RollValue) -> RollValue:
        """Combines the given rolls using the value and tag combiners

        Args:
            *rolls (RollValue): the rolls to combine

        Returns:
            RollValue: the combined roll
        """
        return {
            "value": v_combiner(*rolls),
            "probability": reduce(lambda a, b: a * b, [r["probability"] for r in rolls], 1),
            "tags": tag_combiner(*rolls)
        }
    
    return combiner


def combiner_from_value_combiner(v_combiner: VarargsCallable[RollValue, int]) -> VarargsCallable[RollValue, RollValue]:
    """Creates a combiner function from a value combiner

    Args:
        v_combiner (VarargsCallable[RollValue, RollValue]): the value combiner

    Returns:
        VarargsCallable[RollValue, RollValue]: the combiner function
    """
    return combiner_from_value_and_tag_combiner(v_combiner, lambda *rolls: tag_combiner_additive(*[r["tags"] for r in rolls]))


def value_combiner(v_combiner: VarargsCallable[RollValue, int]) -> VarargsCallable[RollValue, RollValue]:
    """Decorator Alias for combiner_from_value_combiner

    Args:
        v_combiner (VarargsCallable[RollValue, RollValue]): the value combiner

    Returns:
        VarargsCallable[RollValue, RollValue]: the combiner function
    """
    result = combiner_from_value_combiner(v_combiner)
    result.__doc__ = v_combiner.__doc__
    
    return result


# Default Combiners

@value_combiner
def combiner_add(*values: RollValue) -> int:
    """Combines the given values by adding them

    Args:
        values (RollValue): the values to combine

    Returns:
        int: the sum of the parameters
    """
    return sum([v["value"] for v in values])


@value_combiner
def combiner_sub(*values: RollValue) -> int:
    """Combines the given values by subtracting them

    Args:
        values (RollValue): the values to combine

    Returns:
        int: the difference of the parameters
    """
    return values[0]["value"] - sum([v["value"] for v in values[1:]])

@value_combiner
def combiner_mul(*values: RollValue) -> int:
    """Combines the given values by multiplying them

    Args:
        values (RollValue): the values to combine

    Returns:
        int: the product of the parameters
    """
    return reduce(lambda a, b: a * b, [v["value"] for v in values], 1)


@value_combiner
def combiner_div_round(*values: RollValue) -> int:
    """Combines the given values by dividing them

    Args:
        values (RollValue): the values to combine

    Returns:
        int: the quotient of the parameters
    """
    return round(values[0]["value"] / reduce(lambda a, b: a * b, [v["value"] for v in values[1:]], 1))


@value_combiner
def combiner_div_floor(*values: RollValue) -> int:
    """Combines the given values by dividing them

    Args:
        values (RollValue): the values to combine

    Returns:
        int: the quotient of the parameters
    """
    return values[0]["value"] // reduce(lambda a, b: a * b, [v["value"] for v in values[1:]], 1)

@value_combiner
def combiner_pow(*values: RollValue) -> int:
    """Combines the given values by exponentiating them. Only the first two values are used.

    Args:
        values (RollValue): the values to combine

    Returns:
        int: the exponentiation of the parameters
    """
    return values[0]["value"] ** values[1]["value"]

@value_combiner
def combiner_mod(*values: RollValue) -> int:
    """Combines the given values by taking the first value modulo the second value

    Args:
        values (RollValue): the values to combine

    Returns:
        int: the modulo of the parameters
    """
    return values[0]["value"] % values[1]["value"]