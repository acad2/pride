def logistic_map(x, r=3.57):
    while True:
        x = (r * x * 1.0) - (r * x * x)
        yield x
        
def test_logistic_map():
    generator = logistic_map(.4)
    outputs = [next(generator) for count in range(128)]
    print outputs
    
if __name__ == "__main__":
    test_logistic_map()
    