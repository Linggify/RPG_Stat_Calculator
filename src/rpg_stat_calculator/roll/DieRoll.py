
from typing import Dict, List, Union

from .roll_types import RollValue, Distribution
from .BaseRoll import BaseRoll


class DieRoll(BaseRoll):
    """Represents a roll of a die.
    """
    
    def __init__(self, sides: Union[int, List[Union[int, RollValue]]], **tags: Union[int, List[int]]):
        """Creates a new DieRoll with the given sides and tags.

        Args:
            sides (Union[int, List[int], List[RollValue]]): the sides of a die
            
        """
        # create sides array
        tmp_sides: List[Union[int, RollValue]] = []
        if isinstance(sides, int):
            tmp_sides = [i for i in range(1, sides + 1)]
        else:
            tmp_sides = sides

        # convert integer sides to roll sides
        probability_remainder = 1 - sum([side["probability"] for side in tmp_sides if isinstance(side, dict)])
        sides_to_convert = sum([1 for side in tmp_sides if isinstance(side, int)])
        converted_probability = probability_remainder / sides_to_convert
        roll_sides: List[RollValue] = [{"value": side, "probability": converted_probability, "tags": {}} if isinstance(side, int) else side for side in tmp_sides]
        
        def ensureList(value: Union[int, List[int]]) -> List[int]:
            if isinstance(value, int):
                return [value]
            else:
                return value
        
        # apply the specified tags
        self.sides: List[RollValue] = [{
            "value": side["value"],
            "probability": side["probability"],
            "tags": {**side["tags"], **{tag: 1 for tag in tags.keys() if side["value"] in ensureList(tags[tag])}}
        } for side in roll_sides]
        
        
    def get_distribution(self) -> Distribution:
        return self.sides # the sides calculated in the constructor are the distribution