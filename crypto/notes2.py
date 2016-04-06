C = M xor R1 xor R2 xor Rp
R1 = S_BOX[state1 xor ephemeral_byte1]
state1 = M` xor K xor RC
RC = S_BOX[Ti xor Pi]
Ti = 1...N
Pi in (1...N)!
ephemeral_byte1 = Entropy1 xor state1
Entropy1 = Ki xor RC

Entropy1, Ki, RC, ephemeral_byte1, Pi, Ti, state1, R1, C, M, R2, Rp