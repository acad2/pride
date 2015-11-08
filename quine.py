import inspect
def handle_source(source):
    function_calls = []
    for line in source.split('\n'):
        for symbol in line.split():
            while '(' in symbol:
                name, symbol = symbol.split('(', 1)
                if name and ')' not in name and '[' not in name:
                    function_calls.append(name)
    print function_calls
        
handle_source(inspect.getsource(handle_source))