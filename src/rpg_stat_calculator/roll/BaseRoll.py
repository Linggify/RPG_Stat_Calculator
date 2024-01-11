import numpy
from typing import Any, List
from .roll_types import Distribution, RollValue, VarargsCallable
from .combiners import combiner_add, combiner_div_round, combiner_from_value_combiner, combiner_mod, combiner_pow, combiner_sub, combiner_mul


class BaseRoll:
    """Base class of all Rolls. Provides posibility for combining distributions of other rolls or create new ones. These rolls can be combined with +/- and *// to create a roll pattern.
    """
    
    @staticmethod
    def ensure_roll(roll: Any) -> 'BaseRoll':
        """Ensures that the given value is a BaseRoll. If it is an int, it is converted to a ConstantRoll. Otherwise, a TypeError is raised.

        Args:
            roll (Any): the roll to convert

        Raises:
            TypeError: if the roll is not of type int or BaseRoll

        Returns:
            BaseRoll: the roll as a BaseRoll
        """
        if isinstance(roll, BaseRoll):
            return roll
        if isinstance(roll, int):
            return BaseRoll(combiner=lambda *args: {"value": roll, "probability": 1, "tags": {}})
        else:
            raise NotImplementedError(f"Cannot convert {roll} to a BaseRoll")
    
    def __init__(self, *rolls: 'BaseRoll', combiner: VarargsCallable[RollValue, RollValue] = lambda *args: args[0]):
        """Creates a new BaseRoll.
        
        Args:
        :param rolls: the rolls to combine
        :param combiner: the function to combine roll values of the rolls. Default always falls back to the first submitted value.
        """
        self.rolls: List[BaseRoll] = list(rolls) or []
        self.combiner = combiner
    
    def get_distribution(self) -> Distribution:
        """Returns a distribution of the possible values of this roll.
        """
        # if there are no rolls, return a single value from the combiner
        if len(self.rolls) == 0:
            return [self.combiner()]
            
        # accumulate the distributions with the combiner function
        dists = [roll.get_distribution() for roll in self.rolls]
        
        dist: Distribution = []
        for index in numpy.ndindex(*[len(d) for d in dists]):
            rolls = [d[index[i]] for i, d in enumerate(dists)]
            n_roll = self.combiner(*rolls)
            
            # find existing roll in distribution with equal value and tags
            existing = next((d for d in dist if d["value"] == n_roll["value"] and all(d["tags"].get(tag, 0) == n_roll["tags"].get(tag, 0) for tag in set(d["tags"].keys()).union(n_roll["tags"].keys()))), None)
            
            if existing is not None:
                existing["probability"] += n_roll["probability"]
            else:
                dist.append(n_roll)
                
        return dist
    
    def simulate(self) -> RollValue:
        """Returns a single value of this roll.
        """
        values = self.get_distribution()
        args = [i for i in range(len(values))]
        probs = [v["probability"] for v in values]

        return values[numpy.random.choice(args, p=probs)]
    
    # operators
    def __add__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_add)
    
    def __radd__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(roll, self, combiner=combiner_add)
    
    def __sub__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_sub)
    
    def __rsub__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(roll, self, combiner=combiner_sub)
    
    def __mul__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_mul)
    
    def __rmul__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(roll, self, combiner=combiner_mul)
    
    def __truediv__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_div_round)
    
    def __rtruediv__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(roll, self, combiner=combiner_div_round)
    
    def __floordiv__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(roll, self, combiner=combiner_div_round)
    
    def __rfloordiv__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(roll, self, combiner=combiner_div_round)
    
    def __pow__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_pow)
    
    def __mod__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_mod)
    
    def __rmod__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(roll, self, combiner=combiner_mod)
    
    def __neg__(self):
        return self.__mul__(-1)
    
    def __lt__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_from_value_combiner(lambda *args: 1 if args[0]["value"] < args[1]["value"] else 0))
    
    def __le__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_from_value_combiner(lambda *args: 1 if args[0]["value"] <= args[1]["value"] else 0))
    
    def __eq__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_from_value_combiner(lambda *args: 1 if args[0]["value"] == args[1]["value"] else 0))
    
    def __ne__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_from_value_combiner(lambda *args: 1 if args[0]["value"] != args[1]["value"] else 0))
    
    def __gt__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_from_value_combiner(lambda *args: 1 if args[0]["value"] > args[1]["value"] else 0))
    
    def __ge__(self, other):
        roll = BaseRoll.ensure_roll(other)
        return BaseRoll(self, roll, combiner=combiner_from_value_combiner(lambda *args: 1 if args[0]["value"] >= args[1]["value"] else 0))