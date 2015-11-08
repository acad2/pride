import inspect
import ast

import base
SOURCE = inspect.getsource(base)

class Function_Call_Finder(ast.NodeVisitor):
    
    def __init__(self, *args, **kwargs):
        super(Function_Call_Finder, self).__init__(*args, **kwargs)
        self.functions = []
        
    def visit_Call(self, node):
        node_type = node.func
        if isinstance(node_type, ast.Name):
            self.functions.append(node_type.id)
        elif isinstance(node_type, ast.Attribute):
            name = []#getattr(node_type.value, "attr", getattr(node_type.value, "id", None))
            print node_type, name
            while isinstance(node_type, ast.Attribute):                
                name.append(getattr(node_type.value, "attr", getattr(node_type.value, "id", '')))
                print "Adding attribute name: ", name[-1]
                node_type = node_type.value
            if isinstance(node_type, ast.Call):
                print "Found call: ", node_type, node_type.func
                node_type = node_type.func
            elif isinstance(node_type, ast.Name):
                name.append(node_type.id)
            
            #assert isinstance(node_type, ast.Name), (node_type, '.'.join(reversed(name)))
            #name.append(node_type.id)
            
            self.functions.append('.'.join(reversed(name)))
        self.generic_visit(node)
        
if __name__ == "__main__":
    finder = Function_Call_Finder()
    finder.visit(ast.parse(SOURCE))
    print finder.functions
    #print SOURCE