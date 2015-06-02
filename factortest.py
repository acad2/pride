"""35
34 + 1
17 17 1
16 16 3
8 8 8 8 3
7 7 7 7 7"""

def factor(number):
    _number, remainder = divmod(number, 2)
    factors = 2
    _number -= 1
    remainder += 1 * factors
    factors *= 2
    _number /= 2
    _number -= 1
    remainder += 1 * factors
    print remainder, _number, factors
    
if __name__ == "__main__":
    factor(35)
    factor(21)
    factor(18)
    factor(14)