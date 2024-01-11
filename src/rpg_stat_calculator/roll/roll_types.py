from typing import Dict, Generic, List, Protocol, TypeAlias, TypeVar, TypedDict


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

T = TypeVar('T', contravariant=True)
V = TypeVar('V', covariant=True)
class VarargsCallable(Generic[T, V], Protocol):
    """A callable that takes a variable number of arguments
    """
    
    def __call__(self, *args: T) -> V:
        ...