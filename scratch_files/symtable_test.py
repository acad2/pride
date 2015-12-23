import inspect
import symtable

def module_symbol_table(module):
    source = inspect.getsource(module)
    return symtable.symtable(source, 'string', 'exec')
    
def unused_imports(symbol_table):
    return [symbol.get_name() for symbol in symbol_table.get_symbols() if 
            symbol.is_imported() and not symbol.is_referenced()]

def class_symbols(symbol_table):
    return [symbol for symbol in symbol_table.get_children() if
            symbol.get_type() == "class"]
            
def function_symbols(symbol_table):
    return [symbol for symbol in symbol_table.get_children() if
            symbol.get_type() == "function"]
            
def test():
    import base
    base_table = module_symbol_table(base)
    _class_symbols = class_symbols(base_table)
    _function_symbols = function_symbols(base_table)
    print _class_symbols
    
    for _class in _class_symbols:
        _function_symbols = function_symbols(_class)
        for _function in _function_symbols:
            if "_" != _function.get_name()[0]:
                print _function.get_name(), _function.get_parameters(), _function.get_locals(), _function.get_frees()
if __name__ == "__main__":
    test()