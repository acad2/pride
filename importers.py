""" Contains import related functions and objects, including the compiler """
import inspect
import sys
import importlib
import contextlib
import types
import imp
import tokenize
import shlex
import string
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
        
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
            Does not include strings located within other strings. """
        quotes = ["'", '"', "'''", '"""']        
        triple_quote_start = triple_quote_end = ignore_count = 0
        source_length = len(source) - 1
        triple_quote_closing = closing_quote = ''
        indices, open_quotes = [], []
        start_index, end_index = {}, {}
        print_stuff = False
        for index, character in enumerate(source):
            if character == '#':
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
            is_triple_quote = _character in quotes                             
            if character in quotes or is_triple_quote:
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
        return indices
    
    @staticmethod    
    def find_symbol(symbol, source, quantity=0):
        strings = [range(start, end + 1) 
                   for start, end in Parser.get_string_indices(source)]
     #   print "Found strings: "
     #   for _range in strings:
     #       print source[_range[0]:_range[-1]], '...', " index: ", _range[0], _range[-1]
        indices = []
        symbol_size = len(symbol)
        source_index = 0
        while symbol in source:
            start = source_index + source.index(symbol)
            for _range in strings:
                if start in _range:
                    end_of_quote = _range[-1]
                    source = source[end_of_quote:]
                    source_index += end_of_quote
                    break
            else: # did not break, symbol is not inside a quote
                end = start + symbol_size
                indices.append((start, end))
                source = source[end:]
                source_index += end
                quantity -= 1
                if not quantity:
                    break
        return indices

    @staticmethod
    def remove_comments(source):
        new_source = []
        progress = 0
        for line in source.split('\n'):
            if '#' in line:
                line = line[:line.index('#')]
            new_source.append(line)
        return '\n'.join(new_source)
        
    @staticmethod
    def extract_code(source):
        """ Returns start/end of all parts of source that are not in quotes. """
        source = Parser.remove_comments(source)
        string_indices = Parser.get_string_indices(source)
        sections = []        
        last_end = 0
        for start, end in Parser.get_string_indices(source):
            sections.append((last_end, start))
            last_end = end
        sections.append((last_end, len(source)))
        return sections

        
class Compiler(object):
    """ Compiles python source to bytecode. Source may be preprocessed.
        This object is automatically instantiated and inserted into
        sys.meta_path as the first entry. """
    def __init__(self, preprocessors=tuple()):
        self.preprocessors = preprocessors
        self.module_source = {}
        
    def find_module(self, module_name, path):
        modules = module_name.split('.')
        loader = None
        end_of_modules = len(modules) - 1
        for count, module in enumerate(modules):
            try:
                _file, path, description = imp.find_module(module, path)
            except ImportError:
                pass
            else:
                if path.split('.')[-1] == "pyd":
                    continue
                if _file:
                    if ".pyc" in path:
                        print "Unable to import {} @ {}; No source, only bytecode available".format(module_name, path)
                        break
                    self.module_source[module_name] = (_file.read(), path)
                    if count == end_of_modules:
                        loader = self
        return loader        
  
    def load_module(self, module_name):
        if module_name not in sys.modules:
            source, path = self.module_source[module_name]
            self.compile_module(module_name, source, path)
        return sys.modules[module_name]
                    
    def compile_module(self, module_name, source, path):
        new_module = types.ModuleType(module_name) 
     #   print '\n\ncompiling: ', module_name
        sys.modules[module_name] = new_module
        new_module.__name__ = module_name
        new_module.__file__ = path
        module_code = self.compile_source(source, module_name)        
        exec module_code in new_module.__dict__           
        return new_module
    
    def preprocess(self, source):
        for preprocessor in self.preprocessors:
            source = preprocessor.handle_source(source)
        return source
        
    def compile_source(self, source, filename=''):
        return compile(self.preprocess(source), filename, 'exec')         
        
        
class Dollar_Sign_Directive(object):
    """ Replaces '$' directive with mpre.objects lookup. This
        facilitates the syntatic sugar $Component, which is
        translated to mpre.objects['Component']. """
        
    def handle_source(self, source):
        delimiters = ['.', ' ', '\t', '(', ')', '\n', ',']
        length = len("mpre.objects['']")
        while '$' in source:
            slice_information = Parser.find_symbol('$', source, 1)
            if not slice_information: # last symbol in source was in a string
                break
            symbol_start, _end = slice_information[0]
           # print "\n\nFound string replacement: ", source[symbol_start-1:_end + 1] + "...", "index: ", symbol_start, _end
            for index, character in enumerate(source[symbol_start:]):
                if character in delimiters:
                    delimiter = delimiters[delimiters.index(character)]
                    end_index = index
                    break
            name = source[symbol_start + 1:symbol_start + end_index]
            replaced = "mpre.objects['{}']".format(name)
            source = ''.join((source[:symbol_start], replaced,
                              source[symbol_start + 1 + len(name):]))
      #  print "Created replacement source: ", source
        return source        
        
  
class New_Keyword(object):
    
    def handle_source(self, source):
        pass
            
            
class AntipatternError(BaseException):
    meaning = "Source code error indicating poor design"
    
operators = r"""+       -       *       **      /       //      %
                <<      >>      &       |       ^       ~
                <       >       <=      >=      ==      !=      <>"""
               
delimiters = r"""(       )       [       ]       {       }      @
                 ,       :       .       `       =       ;
                 +=      -=      *=      /=      //=     %=
                 &=      |=      ^=      >>=     <<=     **="""
                
unused = "$?"

misc = "\'\"\#\\"

special_symbols = misc + unused + delimiters + operators

class Name_Enforcer(object):
    
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
                    