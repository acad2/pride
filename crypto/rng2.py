from utilities import rotate

def rng(key, seed, tweak, tables=4):
    output = bytearray(256)
    state = key[0]
    rows = [rotate(tweak, amount) for amount in range(tables)]
    row_access = [table_index for table_index in range(tables)]
    row_access_indices = tuple(range(1, tables))
    indices = tuple(range(1, 256))
    
    for row_index in reversed(row_access_indices):
        random_index = (state ^ key[row_index]) & (row_index - 1)
        row_access[row_index], row_access[random_index] = row_access[random_index], row_access[row_index]
                
        current_row = rows[row_access[row_index]]
                
        for entry_index in reversed(indices):
            random_entry_index = state & (entry_index - 1)
            current_row[entry_index], current_row[random_entry_index] = current_row[random_entry_index], current_row[entry_index]
            state ^= key[entry_index] ^ entry_index
            key[entry_index] ^= current_row[entry_index] ^ entry_index
            
    while True:
        for row_index in reversed(row_access_indices):
            random_index = state & (row_index - 1)
            row_access[row_index], row_access[random_index] = row_access[random_index], row_access[row_index]
            
            current_row = rows[row_access[row_index]]
            
            for entry_index in reversed(indices):
                random_entry_index = state & (entry_index - 1)
         #       print entry_index, random_entry_index
                current_row[entry_index], current_row[random_entry_index] = current_row[random_entry_index], current_row[entry_index]
                state ^= seed[entry_index]# ^ output[entry_index]
                seed[entry_index] ^= current_row[entry_index] ^ entry_index
                
                output[entry_index] ^= current_row[entry_index]        
        yield bytes(output)
        
import pride.crypto.rng      
class Test_Cipher(pride.crypto.rng.Stream_Cipher):
    
    def random_bytes(self, amount, seed, tweak=None):
        chunks, extra = divmod(amount, 256)
        generator = rng(bytearray(self.key), pride.crypto.rng.null_pad(seed, 256), range(256))
        output = bytearray()
        for count in range(chunks if not extra else chunks + 1):
            output.extend(next(generator))
        return output
        
        
def test_rng():
    key = bytearray("\x00" * 256)
    seed = bytearray("\x00" * 256)
    tweak = range(256)
    generator = rng(key, seed, tweak)
    for output in range(4):        
        print next(generator)
        
    Test_Cipher.test_metrics("\x00" * 256, "\x00" * 256)
        
if __name__ == "__main__":
    test_rng()
    