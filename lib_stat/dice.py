"""Available Dice types
"""

from lib_stat import ConstantRoll, Distribution, MergeRoll, PartialRoll


class DiceRoll(PartialRoll):
    """Partial Roll that simulates a fair dice
    """
    
    def __init__(self, sides: int):
        self.sides = sides
        
    def get_distribution(self) -> Distribution:
        return {i: 1 / self.sides for i in range(1, self.sides + 1)}
    
    def __rmul__(self, other):
        if isinstance(other, int):
            roll = ConstantRoll(0)
            for _ in range(other):
                roll = MergeRoll(roll, self, lambda a, b: a + b)
                
            return roll
        
        return super().__rmul__(other)
    
# dice
d2 = DiceRoll(2)
d3 = DiceRoll(3)
d4 = DiceRoll(4)
d6 = DiceRoll(6)
d8 = DiceRoll(8)
d10 = DiceRoll(10)
d12 = DiceRoll(12)
d20 = DiceRoll(20)