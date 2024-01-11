
from .combiners import combiner_from_value_combiner
from .BaseRoll import BaseRoll


class MaxRoll(BaseRoll):
    """Selects the maximum value of the given rolls
    """
    
    def __init__(self, *rolls: BaseRoll):
        """Creates a new MaxRoll.
        
        Args:
        :param rolls: the rolls to combine
        """
        super().__init__(*rolls, combiner=combiner_from_value_combiner(lambda *args: max([v["value"] for v in args])))