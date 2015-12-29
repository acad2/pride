try:
    import __builtin__
except ImportError:
    import builtins as __builtin__
import imp
import importlib
import sys
import py_compile
import contextlib
import keyword
import operator
import anydbm
import hashlib

import additional_builtins
import additional_keywords
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
def file_contents_swapped(contents, filepath=''):
    """ Enters a context where the data of the supplied file/filepath are the 
        contents specified in the contents argument. After exiting the context,
        the contents are replaced.
        
        Note that if a catastrophe like a power outage occurs, pythons context 
        manager may not be enough to restore the original file contents. """
    with open(filepath, "r+b") as _file:
        original_contents = _file.read()
        _file.truncate(0)
        _file.seek(0)
        _file.write(contents)
        _file.flush()
        try:
            yield
        finally:
            _file.truncate(0)
            _file.seek(0)
            _file.write(original_contents)
            _file.flush()
            _file.close() 
        
@contextlib.contextmanager
def backup(_object, attribute):
    value = getattr(_object, attribute)
    try:
        yield
    finally:
        setattr(_object, attribute, value)
        
class Compiler(object):
    """ Compiles python source to bytecode. Source may be preprocessed.
        This object is automatically instantiated and inserted into
        sys.meta_path as the first entry when pride is imported. """
    def __init__(self, preprocessors=tuple(), patches=None, modify_builtins=None,
                 cache_filename=".py.cache"):
        self._loading = ''
        self.database = anydbm.open(cache_filename, 'c')
        self._outdated = set()
        sys.meta_path.insert(0, self)
        self.patches = patches or {}
        modify_builtins = self.additional_builtins = modify_builtins or {}
        self.path_loader, self.module_source = {}, {}
        
        for name in additional_builtins.__all__:
            setattr(__builtin__, name, getattr(additional_builtins, name))
            
        keyword_preprocessors = []
        for name in additional_keywords.__all__:
            # slice of the leading underscore which is there to prevent the method backend
            # from being preprocessed
            name = name[1:] 
            keyword_preprocessors.append(type(name, (Keyword, ), {"keyword_string" : name}))
            setattr(__builtin__, "_" + name, getattr(additional_keywords, '_' + name))
                    
        _preprocessors = []
        for name in preprocessors:
            _preprocessors.append(name)#resolve_string(name))
            
        self.preprocessors = tuple(_preprocessors + keyword_preprocessors)
        
        for name, package_path in modify_builtins.items():
            setattr(__builtin__, name, resolve_string(package_path))
            
    def find_module(self, module_name, path):
        if module_name == self._loading:
            return None
            
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
                        break # will have to be loaded by regular CPython importer
                    
                    source = _file.read()
                    source_hash = hashlib.sha512(source).digest()
                    try:
                        old_entry = self.database[module_name]
                    except KeyError:
                        old_entry = ''
                        
                    if old_entry[:64] != source_hash:
                        self._outdated.add(module_name)
                        preprocessed_source = self.preprocess(source)
                        self.database[module_name] = source_hash + preprocessed_source
                    else:
                        preprocessed_source = old_entry[64:]
                    self.module_source[module_name] = (preprocessed_source, _path)
                    
                    if count == end_of_modules:
                        loader = self
        return loader    
    
    def load_module(self, module_name):
        if module_name in self.patches:
            print "Loading patch: ", module_name
            resolve_string(self.patches.pop(module_name))()
             
        elif module_name not in sys.modules:
            source, path = self.module_source[module_name]
            #module_code = self.compile(source, path)
            self.compile_module(module_name, source, path)

        return sys.modules[module_name]
                
    def compile_module(self, module_name, source, path):
        if module_name in self._outdated:
            with file_contents_swapped(source, path):
                py_compile.compile(path)
            self._outdated.remove(module_name)
            
        with backup(self, "_loading"):
            self._loading = module_name
            sys.modules[module_name] = importlib.import_module(module_name)

    #def compile_module(self, module_name, module_code, path):
    #    new_module = types.ModuleType(module_name) 
    ##    print '\n\ncompiling: ', module_name
    #    sys.modules[module_name] = new_module
    #    new_module.__name__ = module_name
    #    new_module.__file__ = path
    #    exec module_code in new_module.__dict__
    #    if not hasattr(new_module, "__package__"):
    #        split = module_name.split('.', 1)
    #        if len(split) > 1:
    #            new_module.__package__ = split[0]
    #       # else:
    #       #     print "No package available for: ", module_name
    #    return new_module
    
    def preprocess(self, source):
        for preprocessor in self.preprocessors:
            source = preprocessor.handle_source(source)
        return source
        
    def compile(self, source, filename=''):
        return compile(self.preprocess(source), filename, 'exec')  
        

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
        back_delimit = DELIMITERS + OPERATORS if back_delimit is True else back_delimit
        forward_delimit = DELIMITERS + OPERATORS if forward_delimit is True else forward_delimit
        
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
           # print "Found start of symbol: ", start
            for string_range in strings:
                if start in string_range:
     #               print "Ignoring potential match that is inside string: ", source[string_range[0]:string_range[-1]]
                    source_index += string_range[-1]
                    break
            else: # did not break, symbol is not inside a quote
                # check to make sure it's not in a comment
                back_track = ''.join(reversed(source[source_index:start]))
                comment_index = back_track.find('#')
                newline_index = back_track.find('\n')
                if comment_index > -1 and comment_index < newline_index:
                    source_index += start + 1
                    continue
                    
                end = start + symbol_size
                #print start-1, end, end-start, len(source), symbol, source
                
                is_back_delimited = (start - 1 >= 0 and source[start - 1] in back_delimit or start == 0)
                is_forward_delimited = (end == source_length or source[end + 1] in forward_delimit)
    #            print "->Found potential match: {} in ".format(symbol), source[start-1:end+1], is_back_delimited, is_forward_delimited
                if back_delimit:
                    if is_back_delimited:
                        if forward_delimit:
                            if is_forward_delimited:
    #                            print "Found forward/back delimited ", symbol, (start, end), source[start-1:end], source[start], source[start-1] in delimiters
                                quantity -= 1
                                indices.append((start, end))
                        else:
    #                        print "Found back delimited {}".format(symbol), (start, end)
                            quantity -= 1
                            indices.append((start, end))
    #                else:
   #                     print "Found non properly delimited symbol: {}".format(source[start-1:end])
                elif forward_delimit:
                    if is_forward_delimited:
   #                     print "Found forward delimited ", symbol, (start, end)
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
        
  
class Preprocessor(object):
    """ Base class for establishing interface of preprocessor objects """
    
    @classmethod
    def handle_source(_class, source): pass
    
    
class Preprocess_Decorator(Preprocessor):
     
    @classmethod
    def handle_source(_class, source):
        while "@pride.preprocess" in source:
            index = Parser.find_symbol("@pride.preprocess", source, ' ', " \n\t(", quantity=1)
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
            
  
class Keyword(Preprocessor):
    """ Base class for new keywords. Subclasses should specify a keyword_string
        class attribute. Keyword functionality is defined in pride.keywords. """
    
    @classmethod
    def handle_source(_class, source):
        keyword_string = _class.keyword_string
        string_length = len(keyword_string)   
   #     print "Testing for: ", keyword_string
        while keyword_string in source:
            index = Parser.find_symbol(keyword_string, source, ' ', '')            
            if not index:
                break            
            start, end = index[0]
            
            try:
                if source[start-1] == "_":
                    break
            except IndexError:
                pass
            #print "Found symbol: ", source[start:]    
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
            if has_newline:
                newline_location = line.index("\n")
            else:
                newline_location = len(line) - (string_length + 1)
            
            for _keyword in keyword.kwlist:
        #        print "Replacing keyword: ", _keyword
                line = line.replace(' ' + _keyword + ' ', " ('{}', ".format(_keyword))
            #print "Line after keyword replacement: ", line, line[string_length + 1:string_length + 1 + newline_location]
            arguments = line[string_length + 1:string_length + 1 + newline_location].strip().split()
            arguments[0] = '"' + arguments[0] + '",'
          #  print "Extracted line: ", arguments
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
                _arguments.append(symbol)
            arguments = " ".join(_arguments)
        #    print "\nresolved to arguments: ", arguments
            new_line = ('_' + line[:string_length] + '(' + arguments + ")" + 
                        ("\n" if has_newline else ''))
            #print "Resolved keyword: ", source[:-1]
            source = source[:start] + new_line + source[start + end_of_line + 1:]            
  #          print "preprocessed to new line: ", new_line
        return source
        
        
class Export_Keyword(Keyword): 
    """ Enables the keyword syntax:
        
        export module_name to fully.qualified.domain.name [as name]
        
        Executes the module specified by module name on the remote host running
        at the address obtained by socket.gethostbyname(fully.qualified.domain.name).
        The remote host must be running pride, the network must be configured
        appropriately, and a Shell connection must be made beforehand. 
        
        If the optional as clause is included, the module will be saved 
        under the name specified instead of ran. """
        
    keyword_string = "export"
    