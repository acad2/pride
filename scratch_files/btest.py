def convert_base(number, base, new_base):
    result = []
    while number:
        number, digit = divmod(number, new_base)
        result.append(str(digit))
    return ''.join(reversed(result))
    
if __name__ == "__main__":
    print convert(100, 10, 2)