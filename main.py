from pydoc import resolve
import sys
from typing import Dict
from lib_stat import ConstantRoll, DieRoll, MergeRoll, PartialRoll, RollValue, apply_tag_rule, remove_tags, roll_max

d20 = DieRoll(20, crit=1, crit_fail=20)
d6 = DieRoll(6)

def resolve_dsa_crit(roll):
    
    def resolve_crit_value(roll: RollValue) -> int:
        if roll['tags'].get('crit', 0) >= 2: # in dsa, crits result in the maximum 
            return 0
        
        return roll['value']
        
    
    def resolve_crit_tags(tags: Dict[str, int]) -> Dict[str, int]:
        result = {**tags} # copy tags
        if result.get('crit', 0) >= 2: # if crit is successfull, mark it with tag
            result['resolved_crit'] = 1
        result.pop('crit', None) # delete temporary trackers
        
        return result
        
    
    return MergeRoll(roll,
                    value_resolver=lambda *rolls: resolve_crit_value(rolls[0]),
                    tag_resolver=lambda *rolls: resolve_crit_tags(rolls[0]['tags']))


def resolve_dsa_crit_fail(roll):
    
    def resolve_crit_fail_value(roll: RollValue) -> int:
        if roll['tags'].get('crit_fail', 0) >= 2: # in dsa, crits result in the maximum 
            return sys.maxsize # largest integer, this can never be beaten
        
        return roll['value']
        
    
    def resolve_crit_fail_tags(tags: Dict[str, int]) -> Dict[str, int]:
        result = {**tags} # copy tags
        if result.get('crit_fail', 0) >= 2: # if crit fail, mark it with tag
            result['resolved_crit_fail'] = 1
            
        result.pop('crit_fail', None) # delete temporary trackers
        
        return result
        
    
    return MergeRoll(roll,
                    value_resolver=lambda *rolls: resolve_crit_fail_value(rolls[0]),
                    tag_resolver=lambda *rolls: resolve_crit_fail_tags(rolls[0]['tags']))


def apply_dsa_tag_rules(roll):
    return resolve_dsa_crit_fail(resolve_dsa_crit(roll))

# dsa ability roll
a1 = 14
a2 = 14
a3 = 14
cv = 10

dsa_roll = apply_dsa_tag_rules(roll_max(a1, d20) - a1 + roll_max(a2, d20) - a2 + roll_max(a3, d20) - a3) <= cv
print(dsa_roll.get_distribution())

# dsa attack roll
at = 17
vw = 4
tp = d6 + 7
dsa_attack_roll = (d20 < at) * (d20 > vw) * tp
#print(dsa_attack_roll.get_distribution())