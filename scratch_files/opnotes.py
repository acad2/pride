# output: 0 3/4 of the time and 1 1/4 of the time
# if the output is 1, the inputs are known 
_and = {(0, 0) : 0, (1, 0) : 0, (0, 1) : 0, (1, 1) : 1}

# output: 1 3/4 of the time and 0 1/4 of the time
# if the output is 0, the inputs are known
_or = {(0, 0) : 0, (1, 0) : 1, (0, 1) : 1, (1, 1) : 1}

# output: 1 2/4 of the time and 0 2/4 of the time
# 50% chance of guessing correctly based on output
xor = {(0, 0) : 0, (1, 0) : 1, (0, 1) : 1, (1, 1) : 0}

# same as above
not_and = {(0, 0) : 0, (1, 0) : 1, (0, 1) : 1, (1, 1) : 0}

# output: 1 4/4 of the time
# output is always 1. input is completely ambiguous
not_or = {(0, 0) : 1, (1, 0) : 1, (0, 1) : 1, (1, 1) : 1}

# output: 1 1/4 of the time, 0 3/4 of the time
# if the output is 0, the inputs are known
not_a_and_not_b = {(0, 0) : 1, (1, 0): 0, (0, 1) : 0, (1, 1) : 0}

# aka material implication
# output: 1 3/4 of the time, 0 1/4 of the time
# if the output is 0, the inputs are known
not_a_or_b = {(0, 0) : 1, (1, 0) : 0, (0, 1) : 1, (1, 1) : 1}

# aka equivalnce
not_a_xor_b