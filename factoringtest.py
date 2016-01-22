import decimal
from math import floor

def factor_modulus(N):
    guess = int(floor(decimal.Decimal(N).sqrt()))
    if not N % guess:
        return guess
        
    if not guess % 2:
        guess -= 1
    while True:
        if not N % guess:
            return guess, N / guess
        else:
            guess -= 2
            
N = int(''.join(str(ord(char)) for char in 
        """MIGHAoGBAN01lQw6DEtRySBBm+Sxl2ivcYmNB6UHovD1m4JOzZKXdHSg/V2S8j5q
        #8nb42Up17iYluPqTBxJH49JzoRqc3lGN4QtiSgQYI0DK9dkYlUIJcqdlYtcefhHH
        #w7hXtOHOTDx6ffAZaIx8j2BlmtQAZHqSBXRp0Uy4xPyfXMHdbP0DAgEC"""))

print factor_modulus(N)        