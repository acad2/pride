""" Contains import related functions and objects, including the compiler """
import os
import inspect
import sys
import importlib
import contextlib
import types
import imp
import tokenize
import shlex
import string
import operator
import textwrap
import keyword
import py_compile
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
  
  
OPERATORS = ('+', '-', '*', '**', '/', '//', '%', '<<', '>>', '&', '|', '^',
             '~', '<', '>', '<=', '>=', '==', '!=', '<>')
               
DELIMITERS = ('(', ')', '[', ']', '{', '}', '@', ',', ':', '.', '`', '=',
              ';', '$', '+=', '-=', '*=', '/=', '//=', '%=', '&=', '|=', 
              '^=', ">>=", "<<=", "**=", ' ', '\n')
                
unused = ('$', '?')

misc = ("\'", "\"", "\#", "\\")

special_symbols = misc + unused + DELIMITERS + OPERATORS
               
def split_reference(reference):
    assert reference
    for index, character in enumerate(reversed(reference)):
        try:
            number = int(character)
        except ValueError:
            break
    try:
        number = int(reference[-index:])
    except ValueError:
        number = 0
    return (reference[:index], number)
        
class From_Disk(object):
        
    def __init__(self, modules=tuple()):
        self.modules = modules
        
    def find_module(self, module_name, path):
        if not self.modules or module_name in self.modules:
            return self
        return None
        
    def load_module(self, module_name):
        del sys.modules[module_name]
        sys.modules[module_name] = module = importlib.import_module(module_name)
        return module
            
    
#class Dollar_Sign_Directive(Preprocessor):
#    """ Currently NOT used. May become deprcated.
#    
#        Replaces '$' directive with pride.objects lookup. This
#        facilitates the syntatic sugar $Component, which is
#        translated to pride.objects['Component']. """
#        
#    def handle_source(self, source):
#        return Parser.replace_symbol('$', source, "pride.objects[{}]", False, False)     
#        
#
#class Dereference_Macro(Preprocessor):
#    """ Currently NOT used. May become deprecated.
#    
#        Facilitates the macro for dereferencing instance names. Source
#        handled by this object will have '/' lookup chains resolved to
#        a name resolution function with the instance names as arguments.
#        Example:
#            
#            /Python/Network/Rpc_Server/Rpc_Socket1
#            # resolves to
#            pride.objects["/Python"].objects["Network"][0].objects["Rpc_Server"][0].objects["Rpc_Socket"][1]
#            
#            self/Network/Rpc_Server/Rpc_Socket1
#            self.objects["Network"][0].objects["Rpc_Server"][0].objects["Rpc_Socket"][1]"""
#        
#    def handle_source(self, source):
#        delimiters = DELIMITERS + OPERATORS
#        ignore_count = source_index = 0
#        reference_start = None
#        quote_open = is_string = False
#        parenthesis_open = 0
#        while '/' in source[source_index:]:
#            indices = Parser.find_symbol('/', source, back_delimit=False,
#                                         forward_delimit=False, start_index=source_index)
#            if not indices:
#                break  
#            #start, end = indices[0]
#            #progress = 0
#            #lines = []
#            #for line in source.split('\n'):
#            #    progress += len(line)
#            #    if start <= progress:
#            #        new_line = ''
#            #        try:
#            #            equals, _line = line.split('=')
#            #        except ValueError:
#            #            pass
#            #        else:
#            #            new_line += equals + '='
#            #        
#            #        new_line += "pride.dereference(packed_args=("
#            #        names = _line.split("/")
#            #        for name in names:
#            #            if '"' in name or "'" in name:
#            #                new_line += str(split_reference(name)) + ", "
#            #            else:
#            #                new_line += "split_reference({}), ".format(name)
#            #        new_line = new_line[:2] + "))"
#            #        lines.append
#
#
#
#
#
#
#
#                
#            name = ''
#            names = []
#            start, end = indices[0]
#            #print "Looking for names in: ", source[end:]
#            # look for the attribute/name before the /
#        #    _name = ''
#        #    for pre_name_index, character in enumerate(reversed(source[:start])):
#        #        print "Testing index: ", pre_name_index, character
#        #        if character in delimiters and character != '.':
#        #            print "Breaking because of: ", character
#        #            break
#        #        print "Adding character to name: ", character
#        #        _name += character
#        #    names.append((''.join(reversed(_name)), False))
#            line = ''
#        #    end_of_
#        #    for character in enumerate(source[end:]):
#        #        current_index = end + index
#        #        _character = source[current_index:current_index+2]
#        #        __character = source[current_index:current_index+3]            
#        #        if character in delimiters or _character
#            
#        #    print "Added prefix name: ", names[0]   
#            for index, character in enumerate(source[end:]):
#                if ignore_count:
#                    ignore_count -= 1
#                    continue
#                current_index = end + index
#                _character = source[current_index:current_index+2]
#                __character = source[current_index:current_index+3]
#                if _character == '/':
#                    #for __character_ in source[index+2:]:
#                    #    if __character_ in (' ', '\t', '('):
#                    #        if __character_ == '(':
#                    #            
#                    #            parenthesis_open += 1
#                    #    elif __character_ in delimiters:
#                    #        break
#                    
#                    print "Next arrow, Finished last name: ", name
#                    source_index = index
#                    names.append((name, is_string))
#                    name = ''
#                    is_string = False
#                    ignore_count += 1
#                elif (character in delimiters or _character in delimiters or
#                      __character in delimiters) and character != '.':
#                    print "Found delimiter: ", character, _character, __character, name
#                    names.append((name, is_string))
#                    name = ''
#                    source_index = index
#                    is_string = False
#                    break
#                    #if character == '(':
#                    #    if not name:
#                    #        parenthesis_open += 1
#                    #    elif parenthesis_open:
#                    #        parenthesis_open += 1
#                    #        
#                    #if parenthesis_open:
#                    #    print "Adding character inside ()", character, name
#                    #    name += character
#                        
#                    #if character == ')':
#                    #    parenthesis_open -= 1
#                    #    if not parenthesis_open:
#                    #        break
#                    #else:
#                    #    break
#                else:
#                    if character in ('"', "'"):
#                        if not quote_open:
#                            quote_open = True
#                            is_string = True
#                        else:
#                            quote_open = False
#                    else:
#                        print "Adding character: ", character, name
#                        source_index = index
#                        name += character
#            if name:
#                names.append((name, is_string))
#                index += 1
#            source_index = end + index 
#            arg_string = "packed_args=("
#            #replacement = "pride.dereference(packed_args=("
#            for name, is_string in names:
#                if name:
#                    if not is_string:                    
#                        arg_string += "pride.split_reference({}), ".format(name)
#                    else:
#                        arg_string += str(split_reference(name)) + ", "
#            arg_string = arg_string[:-2] + "))" # replace the last ", " with "))" 
#            replacement = "pride.dereference(" + arg_string
#            _end = start# - len(names[0][0])
#            source = source[:_end] + replacement + source[end + index:]
#            print "\nSource:", source
#        return source
#        
#        
#class Function_Inliner(Preprocessor):
#
#    def handle_source(self, source):
#        delimiters = DELIMITERS + OPERATORS
#        _source = Parser.replace_symbol('$', source, '{}')
#        print source
#        print _source
#        bytecode = compile(_source, 'inline_test', 'exec')
#        module = sys.meta_path[0].compile_module('', bytecode, '')
#        sources = []
#        for start, end in Parser.find_symbol('$', source):
#            for end_of_symbol, character in enumerate(source[end:]):
#                if character in delimiters:
#                    break
#            function_name = source[end:end + end_of_symbol + 1]
#            print 'Function name: ', function_name, end, end + end_of_symbol + 1
#            function_source = inspect.getsource(getattr(module, function_name))
#            sources.append((function_name, Parser.extract_code(function_source)))
#            
#        for function_name, inline_source in sources:
#            source = Parser.replace_symbol('$' + function_name, inline_source)
#        print "Returning: ", source
#        return source
#        
#                            
#class AntipatternError(BaseException):
#    meaning = "Source code error indicating poor design"
#    
#
#class Name_Enforcer(Preprocessor):
#    
#    cache = {}
#    
#    def is_variable_name(self, token):
#        if token in self.cache:
#            return True
#            
#        if ' ' not in token:
#            for character in special_symbols:
#                if character in token:
#                    break
#            else:
#                self.cache[token] = True
#                return True        
#
#    def handle_source(self, source): 
#        strings = Parser.get_string_indices(source)
#        source_pieces = []
#        last_end = 0
#        for _range in strings:
#            source_pieces.append(source[last_end:_range[0]])
#            last_end = _range[1]
#        source_pieces.append(source[last_end:])
#        _source = '\n'.join(source_pieces)
#        for name in _source.split():
#            print name
#            if self.is_variable_name(name):            
#                if len(name) < 3 or (name in string.letters and 
#                                     name not in ('x', 'y', 'z', 't')):
#                    raise AntipatternError("Short variable name '{}'".format(name))
#                    
#                _name =(name.replace('a', '').replace('e', '').replace('i', '')
#                        .replace('o', '').replace('u', '').replace('y', ''))
#                if _name == name:
#                    raise AntipatternError("Encountered variable name without vowels '{}'".format(name))                   
#        return source                 
                    
if __name__ == "__main__":  
    #export_keyword = Export_Keyword()
    import socket
    host_name = socket.getfqdn()
    test_source = "export payload for {}\n".format(host_name)# as some_other_name".format(host_name)# with dynamic_keywords if variable_1 is True and variable_2 is not 0".format(host_name)
    print test_source
    print "Testing test source in importers"
    print Export_Keyword.handle_source(test_source)