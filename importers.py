""" Contains import related functions and objects, including the compiler """
try:
    import __builtin__
except ImportError:
    import builtins as __builtin__
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
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
  
import additional_builtins
resolve_string = additional_builtins.resolve_string
  
OPERATORS = ('+', '-', '*', '**', '/', '//', '%', '<<', '>>', '&', '|', '^',
             '~', '<', '>', '<=', '>=', '==', '!=', '<>')
               
DELIMITERS = ('(', ')', '[', ']', '{', '}', '@', ',', ':', '.', '`', '=',
              ';', '$', '+=', '-=', '*=', '/=', '//=', '%=', '&=', '|=', 
              '^=', ">>=", "<<=", "**=", ' ', '\n')
                
unused = ('$', '?')

misc = ("\'", "\"", "\#", "\\")

special_symbols = misc + unused + DELIMITERS + OPERATORS
  
@contextlib.contextmanager
def sys_meta_path_switched(new_meta_path):
    backup = sys.meta_path
    sys.meta_path = new_meta_path
    try:
        yield
    finally:
        sys.meta_path = backup

@contextlib.contextmanager        
def imports_from_disk():
    with sys_meta_path_switched([From_Disk()]):
        yield
 
def split_instance_name(instance_name):
    assert instance_name
    for index, character in enumerate(reversed(instance_name)):
        try:
            number = int(character)
        except ValueError:
            break
    try:
        number = int(instance_name[-index:])
    except ValueError:
        number = 0
    return (instance_name[:index], number)
        
        
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
        
       
class Parser(object):
    
    @staticmethod
    def get_string_indices(source):
        """ Return a list of indices of strings found in source. 
            Includes substrings located within other strings. """
        quote_symbols = ["'", '"', "'''", '"""']        
        triple_quote_start = triple_quote_end = ignore_count = 0
        source_length = len(source) - 1
        triple_quote_closing = closing_quote = ''
        indices, open_quotes = [], []
        start_index, end_index = {}, {}
    #    print "Getting strings from: ", len(source), source
        for index, character in enumerate(source):
         #   print index, len(source)
            if character == '\\': # backslash
                ignore_count += 2                
            elif character == '#':
                try:
                    newline = source[index:].index('\n') + index
                except ValueError: # comment with no newline at end of file
                    break
                else:
                    ignore_count = newline - index
                                
            if ignore_count:
                ignore_count -= 1
                continue
            _character = source[index:index + min(3, source_length - index)]
            is_triple_quote = _character in quote_symbols                    
            if is_triple_quote or character in quote_symbols:
                if is_triple_quote:
                    character = _character
                    ignore_count = 2
                    
                if character not in start_index:
                    open_quotes.append(character)
                    start_index[character] = index
                else:
                    end_index[character] = index + len(character)
                    
            if character in end_index:
                indices.append((start_index[character], end_index[character]))
                layer = open_quotes.index(character)
                for __character in open_quotes[layer:]:
                    end_index.pop(__character, None)
                    start_index.pop(__character, None)
                open_quotes = open_quotes[:layer]
        return sorted(indices, key=operator.itemgetter(0))
    
    @staticmethod    
    def find_symbol(symbol, source, back_delimit=True, forward_delimit=True, 
                    start_index=0, quantity=1):
        """ Locates all occurrences of symbol inside source up to the given
            quantity of times. Matches only count if the symbol is not inside
            a quote or behind a comment. """
        strings = [range(start, end + 1) 
                   for start, end in Parser.get_string_indices(source)]
        delimiters = DELIMITERS + OPERATORS
        #print "Found strings: "
        #for _range in strings[:len(strings) / 2]:
        #    print source[_range[0]:_range[-1]], '...', " index: ", _range[0], _range[-1]
        indices = []
        symbol_size = len(symbol)
        source_index = start_index
        source_length = len(source)
        #print "# Trying to find: {} ".format(symbol), start_index, len(source)#, source[source_index:]
        while symbol in source[source_index:] and quantity > 0:  
            start = source.index(symbol, source_index)
    #        print "Found start of symbol: ", start
            for string_range in strings:
                if start in string_range:
     #               print "Ignoring potential match that is inside string: ", source[string_range[0]:string_range[-1]]
                    source_index += string_range[-1]
                    break
            else: # did not break, symbol is not inside a quote
                end = start + symbol_size
                #print start-1, end, end-start, len(source), symbol, source
     #           print "->Found potential match: {} in ".format(symbol), source[start-1:end+1]
                is_back_delimited = (start - 1 >= 0 and source[start-1] in delimiters or start == 0)
                is_forward_delimited = (end == source_length or source[end] in delimiters)
                if back_delimit:
                    if is_back_delimited:
                        if forward_delimit:
                            if is_forward_delimited:
    #                            print "Found forward/back delimited ", symbol, (start, end)
                                quantity -= 1
                                indices.append((start, end))
                        else:
    #                        print "Found back delimited {}".format(symbol), (start, end)
                            quantity -= 1
                            indices.append((start, end))                
                elif forward_delimit:
                    if is_forward_delimited:
    #                    print "Found forward delimited ", symbol, (start, end)
                        quantity -= 1
                        indices.append((start, end))
                elif not (back_delimit or forward_delimit):
    #                print "Found non delimited ", symbol, (start, end)
                    quantity -= 1
                    indices.append((start, end))
    #            else:
    #                print "Found non properly delimited symbol: {} at {}".format(symbol, (start, end))
    #                print source[start-20:end+20], (start - 1 >= 0 and source[start-1] in delimiters), start ==0
                source_index = end
    #        print "Incrementing index by {} to {}".format(end, source_index)
        return indices
        
    @staticmethod
    def replace_symbol(symbol, source, replacement, back_delimit=True,
                       forward_delimit=True, start_index=0):
        delimiters = DELIMITERS + OPERATORS
        #print "\nReplacing {} with {}".format(symbol, replacement)
        _count = 0
        while symbol in source:
            slice_information = Parser.find_symbol(symbol, source, back_delimit,
                                                   forward_delimit, start_index)
            if not slice_information: # last symbol in source was in a string
        #        print "last symbol in source was a string", slice_information
                break
            symbol_start, _end = slice_information[0]
          #  print "\nFound string replacement: ...", source[symbol_start-10:_end+10] + "...", "index: ", symbol_start, _end
            ignore_count = 0
            size = len(source[symbol_start + 1:]) - 1
            for index, character in enumerate(source[symbol_start + 1:]):
                if ignore_count:
                    ignore_count -= 1
                    continue
                if index < size:
                    _character = character + source[symbol_start + 2 + index]
                else:
                    _character = character
                if character in delimiters:
                    if _character == "->":
                        ignore_count += 2
                    else:
        #                print "Found word delimiter: ", character, source[symbol_start:symbol_start + index + 1]
                        delimiter = delimiters[delimiters.index(character)]
                        end_index = index
                        break
            else:
                end_index = index
            name = source[symbol_start + 1:symbol_start + end_index + 1]
            replaced = replacement.format(name)
        #    print "Created replacement symbol: ", replacement
            source = ''.join((source[:symbol_start], replaced,
                              source[symbol_start + 1 + len(name):]))
            _count += 1
            start_index = symbol_start + 1 + len(replaced)
      #  assert symbol not in source, source
    
      #  print "Created replacement source: ", source
        return source 
        
    @staticmethod
    def remove_comments(source):
        new_source = []
        for line in source.split('\n'):
            if '#' in line:
                _line = line[:line.index('#')]
                if not _line.replace('\t', '    ').replace('    ', ''):
                    #print "removing comment line: ", line
                    continue
            new_source.append(line)
        return '\n'.join(new_source)
        
    @staticmethod
    def remove_docstring(source):
        """ Returns source without docstring """
        indices = Parser.get_string_indices(source)
        result = source
        if indices:
            start_of_string, end_of_string = indices[0]
            if (source[start_of_string-4:start_of_string] == '    ' or
                source[start_of_string-1] == '\t'):
                result = source[:start_of_string] + source[end_of_string:]            
        return result
      
    @staticmethod
    def remove_header(source):
        """ Returns source without a class or def header. """
        if not (':' in source and '\n' in source and 
                ('    ' in source or '\t' in source)):
            raise ValueError("Could not find class or def header in {}".format(source))      
        colon_found = newline_found = indent_found = False 
        enclosing_characters = ('{', '[', '(')
        end_enclosing_characters = ('}', ']', ')')
        enclose_count = 0
        for index, character in enumerate(source):
            if character in enclosing_characters:
            #    print "Found opening character: ", character
                enclose_count += 1
            elif character in end_enclosing_characters:
           #     print "Found closing character: ", character
                enclose_count -= 1
            if not enclose_count:
                if character == ':' and not colon_found:
                    colon_found = True
                elif character == '\n':
                    newline_found = True
                elif character == '\t' or source[index:index+4] == "    ":
                    indent_found = True
            if colon_found and newline_found and indent_found:
                end_of_header = index
                break
        return source[end_of_header:]
                
    @staticmethod
    def extract_code(source):
        """ Returns source without header, comments, or docstring. """
        return Parser.remove_docstring(Parser.remove_header(Parser.remove_comments(source)))
        
        
class Compiler(object):
    """ Compiles python source to bytecode. Source may be preprocessed.
        This object is automatically instantiated and inserted into
        sys.meta_path as the first entry when pride is imported. """
    def __init__(self, preprocessors=tuple(), patches=None, modify_builtins=None):
        self.preprocessors = preprocessors
        self.patches = patches or {}
        modify_builtins = self.additional_builtins = modify_builtins or {}
        self.path_loader, self.module_source = {}, {}
        
        for name in additional_builtins.__all__:
            setattr(__builtin__, name, getattr(additional_builtins, name))
            
        for name, package_path in modify_builtins.items():
            setattr(__builtin__, name, resolve_string(package_path))
            
    def find_module(self, module_name, path):
        modules = module_name.split('.')
        loader = None
        end_of_modules = len(modules) - 1
        for count, module in enumerate(modules):
            try:
                _file, _path, description = imp.find_module(module, path)
            except ImportError:
                pass
            else:
                if _path.split('.')[-1] == "pyd":
                    continue
                if _file:
                    if ".pyc" in _path:
                        print "Unable to import {} @ {}; No source, only bytecode available".format(module_name, _path)
                        break
                    self.module_source[module_name] = (_file.read(), _path)
                    if count == end_of_modules:
                        loader = self
        return loader    
    
    def load_module(self, module_name):
        if module_name in self.patches:
            print "Loading patch: ", module_name
            resolve_string(self.patches.pop(module_name))()
             
        elif module_name not in sys.modules:
            source, path = self.module_source[module_name]
            module_code = self.compile(source, path)
            self.compile_module(module_name, module_code, path)

        return sys.modules[module_name]
                    
    def compile_module(self, module_name, module_code, path):
        new_module = types.ModuleType(module_name) 
    #    print '\n\ncompiling: ', module_name
        sys.modules[module_name] = new_module
        new_module.__name__ = module_name
        new_module.__file__ = path
        exec module_code in new_module.__dict__
        if not hasattr(new_module, "__package__"):
            split = module_name.split('.', 1)
            if len(split) > 1:
                new_module.__package__ = split[0]
            else:
                print "No package available for: ", module_name
        return new_module
    
    def preprocess(self, source):
        for preprocessor in self.preprocessors:
            source = preprocessor.handle_source(source)
        return source
        
    def compile(self, source, filename=''):
        return compile(self.preprocess(source), filename, 'exec')         
        
  
class Preprocessor(object):
    """ Base class for establishing interface of preprocessor objects """
    
    def handle_source(self, source): pass
    
    
class Preprocess_Decorator(Preprocessor):
        
    def handle_source(self, source):
        while "@pride.preprocess" in source:
            index = Parser.find_symbol("@pride.preprocess", source, True, False, quantity=1)
            if not index:
                break
            start, end = index[0]
            _source = source[end:].split('\n')[1:]
            first_line = _source[0].replace('\t', '    ')
            
            def_index = first_line.index("def")
            indentation = first_line[:def_index].count("    ")
            name = first_line[def_index + 4:first_line.index('(')]
            function_source = [first_line]
            for line in _source[1:]:
                function_source.append(line)
                line = line.replace('\t', "    ")
                _indentation = 0
                while line[:4] == "    ":
                    _indentation += 1
                    line = line[4:]
                if _indentation == indentation or not line.strip():
                    break
            code = compile(textwrap.dedent('\n'.join(function_source)), "preprocessor_decorator", "exec")
            namespace = {}
            exec code in namespace, namespace
            new_source = namespace[name]()
            assert new_source, "Preprocessor function failed to return new source"
            #print source[:start] + new_source
            #print 'end of source next\n'
            #print source[end + sum((len(line) for line in function_source)) + len("@pride.preprocess"):]
            source = source[:start] + new_source + source[end + sum((len(line) for line in function_source)) + len("@pride.preprocess"):]
            
        return source
            
  
class Export_Keyword(Preprocessor):
    """ Enables the keyword syntax:
        
        export module_name to fully.qualified.domain.name [as name]
        
        Executes the module specified by module name on the remote host running
        at the address obtained by socket.gethostbyname(fully.qualified.domain.name).
        The remote host must be running pride, the network must be configured
        appropriately, and a Shell connection must be made beforehand. 
        
        If the optional as clause is included, the module will be saved 
        under the name specified instead of ran. """
        
    def handle_source(self, source):
        export_length = len("export")        
        while "export" in source:
            index = Parser.find_symbol("export", source, True, True)
            if not index:
                break
            start, end = index[0]            
            try:
                if source[start-1] == "_":
                    break
            except IndexError:
                pass
                
            for end_of_line, character in enumerate(source[start:]):
                if character == "\n":
                    has_newline = True
                    break
            else:
                has_newline = False
                
            # transforms "export module_name for fully.qualified.domain.name as name" to:
            # export module_name, for=fully.qualified.domain.name, as=name \n
            # _export(module_name, for=fully.qualified.domain.name, as=name)\n
            line = source[start:start + end_of_line + 1]
           # print line
            if has_newline:
                newline_location = line.index("\n")
            else:
                newline_location = None
            
            for _keyword in keyword.kwlist:
        #        print "Replacing keyword: ", _keyword
                line = line.replace(' ' + _keyword + ' ', " ('{}', ".format(_keyword))
            arguments = line[export_length + 1:newline_location].strip().split()
            arguments[0] = arguments[0] + ','
       #     print "Extracted line: ", arguments
            _arguments = []
            needs_close = False
            for symbol in arguments:
                if needs_close:                    
                    if '(' == symbol[0]:                        
                        symbol = "'{} ".format(symbol[2:])
                    else:
                        needs_close = False
                        symbol = "'{}'), ".format(symbol)
                if "(" in symbol:
                    needs_close = True
                    #_keyword, _string = symbol.split('=', 1)
                    #symbol = '='.join((_keyword, '"' + _string + '"'))
                _arguments.append(symbol)
            arguments = " ".join(_arguments)
       #     print "\nresolved to arguments: ", arguments
            new_line = ('_' + line[:export_length] + '(' + arguments + ")" + 
                        ("\n" if has_newline else ''))
            #print "Resolved keyword: ", source[:-1]
            source = source[:start] + new_line + source[start + end_of_line + 1:]
            #print "Created new source: ", source
        return source
        
        
class Dollar_Sign_Directive(Preprocessor):
    """ Currently NOT used. May become deprcated.
    
        Replaces '$' directive with pride.objects lookup. This
        facilitates the syntatic sugar $Component, which is
        translated to pride.objects['Component']. """
        
    def handle_source(self, source):
        return Parser.replace_symbol('$', source, "pride.objects[{}]", False, False)     
        

class Dereference_Macro(Preprocessor):
    """ Currently NOT used. May become deprecated.
    
        Facilitates the macro for dereferencing instance names. Source
        handled by this object will have '->' lookup chains resolved to
        a name resolution function with the instance names as arguments.
        Example:
            
            ->Python->Network->Rpc_Server->Rpc_Socket1
            # resolves to
            pride.objects["->Python"].objects["Network"][0].objects["Rpc_Server"][0].objects["Rpc_Socket"][1]
            
            self->Network->Rpc_Server->Rpc_Socket1
            self.objects["Network"][0].objects["Rpc_Server"][0].objects["Rpc_Socket"][1]"""
        
    def handle_source(self, source):
        delimiters = DELIMITERS + OPERATORS
        ignore_count = source_index = 0
        reference_start = None
        quote_open = is_string = False
        parenthesis_open = 0
        while '->' in source[source_index:]:
            indices = Parser.find_symbol('->', source, back_delimit=False,
                                         forward_delimit=False, start_index=source_index)
            if not indices:
                break  
            #start, end = indices[0]
            #progress = 0
            #lines = []
            #for line in source.split('\n'):
            #    progress += len(line)
            #    if start <= progress:
            #        new_line = ''
            #        try:
            #            equals, _line = line.split('=')
            #        except ValueError:
            #            pass
            #        else:
            #            new_line += equals + '='
            #        
            #        new_line += "pride.dereference(packed_args=("
            #        names = _line.split("->")
            #        for name in names:
            #            if '"' in name or "'" in name:
            #                new_line += str(split_instance_name(name)) + ", "
            #            else:
            #                new_line += "split_instance_name({}), ".format(name)
            #        new_line = new_line[:2] + "))"
            #        lines.append







                
            name = ''
            names = []
            start, end = indices[0]
            #print "Looking for names in: ", source[end:]
            # look for the attribute/name before the ->
        #    _name = ''
        #    for pre_name_index, character in enumerate(reversed(source[:start])):
        #        print "Testing index: ", pre_name_index, character
        #        if character in delimiters and character != '.':
        #            print "Breaking because of: ", character
        #            break
        #        print "Adding character to name: ", character
        #        _name += character
        #    names.append((''.join(reversed(_name)), False))
            line = ''
        #    end_of_
        #    for character in enumerate(source[end:]):
        #        current_index = end + index
        #        _character = source[current_index:current_index+2]
        #        __character = source[current_index:current_index+3]            
        #        if character in delimiters or _character
            
        #    print "Added prefix name: ", names[0]   
            for index, character in enumerate(source[end:]):
                if ignore_count:
                    ignore_count -= 1
                    continue
                current_index = end + index
                _character = source[current_index:current_index+2]
                __character = source[current_index:current_index+3]
                if _character == '->':
                    #for __character_ in source[index+2:]:
                    #    if __character_ in (' ', '\t', '('):
                    #        if __character_ == '(':
                    #            
                    #            parenthesis_open += 1
                    #    elif __character_ in delimiters:
                    #        break
                    
                    print "Next arrow, Finished last name: ", name
                    source_index = index
                    names.append((name, is_string))
                    name = ''
                    is_string = False
                    ignore_count += 1
                elif (character in delimiters or _character in delimiters or
                      __character in delimiters) and character != '.':
                    print "Found delimiter: ", character, _character, __character, name
                    names.append((name, is_string))
                    name = ''
                    source_index = index
                    is_string = False
                    break
                    #if character == '(':
                    #    if not name:
                    #        parenthesis_open += 1
                    #    elif parenthesis_open:
                    #        parenthesis_open += 1
                    #        
                    #if parenthesis_open:
                    #    print "Adding character inside ()", character, name
                    #    name += character
                        
                    #if character == ')':
                    #    parenthesis_open -= 1
                    #    if not parenthesis_open:
                    #        break
                    #else:
                    #    break
                else:
                    if character in ('"', "'"):
                        if not quote_open:
                            quote_open = True
                            is_string = True
                        else:
                            quote_open = False
                    else:
                        print "Adding character: ", character, name
                        source_index = index
                        name += character
            if name:
                names.append((name, is_string))
                index += 1
            source_index = end + index 
            arg_string = "packed_args=("
            #replacement = "pride.dereference(packed_args=("
            for name, is_string in names:
                if name:
                    if not is_string:                    
                        arg_string += "pride.split_instance_name({}), ".format(name)
                    else:
                        arg_string += str(split_instance_name(name)) + ", "
            arg_string = arg_string[:-2] + "))" # replace the last ", " with "))" 
            replacement = "pride.dereference(" + arg_string
            _end = start# - len(names[0][0])
            source = source[:_end] + replacement + source[end + index:]
            print "\nSource:", source
        return source
        
        
class Function_Inliner(Preprocessor):

    def handle_source(self, source):
        delimiters = DELIMITERS + OPERATORS
        _source = Parser.replace_symbol('$', source, '{}')
        print source
        print _source
        bytecode = compile(_source, 'inline_test', 'exec')
        module = sys.meta_path[0].compile_module('', bytecode, '')
        sources = []
        for start, end in Parser.find_symbol('$', source):
            for end_of_symbol, character in enumerate(source[end:]):
                if character in delimiters:
                    break
            function_name = source[end:end + end_of_symbol + 1]
            print 'Function name: ', function_name, end, end + end_of_symbol + 1
            function_source = inspect.getsource(getattr(module, function_name))
            sources.append((function_name, Parser.extract_code(function_source)))
            
        for function_name, inline_source in sources:
            source = Parser.replace_symbol('$' + function_name, inline_source)
        print "Returning: ", source
        return source
        
                   
            
class AntipatternError(BaseException):
    meaning = "Source code error indicating poor design"
    

class Name_Enforcer(Preprocessor):
    
    cache = {}
    
    def is_variable_name(self, token):
        if token in self.cache:
            return True
            
        if ' ' not in token:
            for character in special_symbols:
                if character in token:
                    break
            else:
                self.cache[token] = True
                return True        

    def handle_source(self, source): 
        strings = Parser.get_string_indices(source)
        source_pieces = []
        last_end = 0
        for _range in strings:
            source_pieces.append(source[last_end:_range[0]])
            last_end = _range[1]
        source_pieces.append(source[last_end:])
        _source = '\n'.join(source_pieces)
        for name in _source.split():
            print name
            if self.is_variable_name(name):            
                if len(name) < 3 or (name in string.letters and 
                                     name not in ('x', 'y', 'z', 't')):
                    raise AntipatternError("Short variable name '{}'".format(name))
                    
                _name =(name.replace('a', '').replace('e', '').replace('i', '')
                        .replace('o', '').replace('u', '').replace('y', ''))
                if _name == name:
                    raise AntipatternError("Encountered variable name without vowels '{}'".format(name))                   
        return source                 
                    
if __name__ == "__main__":  
    export_keyword = Export_Keyword()
    import socket
    host_name = socket.getfqdn()
    test_source = "export payload for {} as some_other_name with dynamic_keywords if variable_1 is True and variable_2 is not 0".format(host_name)
    print test_source
    print 
    print export_keyword.handle_source(test_source)