from itertools import permutations
from differential import build_difference_distribution_table, find_best_output_differential

def find_best_sbox():
    inputs = tuple(range(3))
    best_differential = (None, None, 0)
    for outputs in permutations(inputs):
        if outputs == inputs:
            continue        
        table1, table2 = build_difference_distribution_table(outputs)
        
        for differential in range(1, 3):            
            info = find_best_output_differential(table1, differential)
            if info[-1] > best_differential[-1]:                
                best_differential = info
                best_outputs = outputs
    print best_differential
    print best_outputs
        
def test_find_best_sbox():
    find_best_sbox()
    
if __name__ == "__main__":
    test_find_best_sbox()