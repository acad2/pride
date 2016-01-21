def identity(number):
    return number
    
def summation(*args):
    output = args[0]
    for number in args[1:]:
        output += number # identity(number)
    return output
    
def multiplication(*args):
    output = args[0]    
    for term in args[1:]:        
        output = summation(*(output for count in range(term)))               
    return output
    
def exponentiation(*args):
    output = args[0]
    for term in args[1:]:        
        output = multiplication(*(output for count in range(term)))
    return output
    
def tetration(*args):
    output = args[0]
    for term in args[1:]:
        output = exponentiation(*(output for count in range(term)))
    return output