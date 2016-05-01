def rotate_two_bytes_left(left, right, amount):     
    amount %= 8  
    return  ((left << amount) & 255) | ((right >> 8 - amount)), (right << amount) & 255 | ((left >> 8 - amount))
    
def rotate_right(left, right, amount):     
    amount %= 8  
    return  (left >> amount) | ((right << (8 - amount))) & 255, ((right >> amount) | ((left << (8 - amount)) & 255))
    
    
left = 150
right = 165
print format(left, 'b').zfill(8), format(right, 'b').zfill(8)
left, right = rotate_right(left, right, 3)
print format(left, 'b').zfill(8), format(right, 'b').zfill(8)



#1001 0110 1010 0101
#1011 0010 1101 0100

 



