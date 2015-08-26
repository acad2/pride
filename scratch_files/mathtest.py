def euclidean_gcd(a, b):
    while b != 0:
        r = a % b
        a = b
        b = r
    return a
    
def euclidean_extended(a, b):
    if b == 0:
        d = a
        x = 1
        y = 0
    else:
        x2 = 1
        x1 = 0
        y2 = 0
        y1 = 1
        while b > 0:
            q, r = divmod(a, b)
            r = a - q * b
            x = x2 - q * x1
            y = y2 - q * y1
            
            a = b
            b = r
            x2 = x1
            x1 = x
            y2 = y1
            y1 = y
        d = a
        x = x2
        y = y2
        return (d, x, y)
if __name__ == "__main__":
    print euclidean_gcd(100, 1300)
    print euclidean_extended(4864, 3458)