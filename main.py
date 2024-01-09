from lib_stat import ConstantRoll, DiceRoll, roll_max

d20 = DiceRoll(20, crit=1, crit_fail=20)
d6 = DiceRoll(6)

# dsa ability roll
a1 = 14
a2 = 14
a3 = 14
cv = 10

dsa_roll = (roll_max(a1, d20) - a1 + roll_max(a2, d20) - a2 + roll_max(a3, d20) - a3) < cv
print(dsa_roll.get_distribution())

# dsa attack roll
at = 17
vw = 4
tp = d6 + 7
dsa_attack_roll = (d20 < at) * (d20 > vw) * tp
#print(dsa_attack_roll.get_distribution())