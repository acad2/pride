def shuffle_row(_bytes, key):
    for index in range(1, len(_bytes)):
        random_index = key & (index - 1)
        _bytes[index], _bytes[random_index] = _bytes[random_index], _bytes[index]
        
def shuffle_column(rows, key, column, row_count):    
    for index in range(1, row_count):        
        random_index = key & (row_count - 1)
        rows[index][column], rows[random_index][column] = rows[random_index][column], rows[index][column]
    
def new_rows(row_size=2, row_count=2):    
    return [range(row_size) for row_number in range(row_count)]
    
def permutation(rows):  
    row_count = len(rows)        
    for row_key, row in enumerate(rows):              
        shuffle_row(row, row_key)
        shuffle_column(rows, row[0], len(rows[0]) - 1, row_count)         
        
def test_permutation():
    rows = new_rows(2, 2)
    outputs = set()
    for round in range(26): 
        print(tuple([row[-1] for row in rows]))
        permutation(rows)
        outputs.add(tuple([row[-1] for row in rows]))
    print len(outputs)
    
if __name__ == "__main__":
    test_permutation()