import os

def update_coordinates(s, x, y, z):
    for n in range(len(s)):                
        x[n] = s[n-2] - s[n-3]
        y[n] = s[n-1] - s[n-2]
        z[n] = s[n] - s [n-1]
        
def test_prng():
    x, y, z = list(bytearray(256)), list(bytearray(256)), list(bytearray(256))
    inputs = bytearray(os.urandom(256))
    update_coordinates(inputs, x, y, z)
    print x
    
if __name__ == "__main__":
    test_prng()
    