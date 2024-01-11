
from .combiners import combiner_from_value_combiner
from .BaseRoll import BaseRoll


class MinRoll(BaseRoll):
    """Selects the minimum value of the given rolls
    """
    
    def __init__(self, *rolls: BaseRoll):
        """Creates a new MinRoll.
        
        Args:
        :param rolls: the rolls to combine
        """
        super().__init__(*rolls, combiner=combiner_from_value_combiner(lambda *args: min([v["value"] for v in args])))