import sys
import time
import inspect
import subprocess
import collections
import contextlib
import importlib
import types
import pickle
import hashlib
import pprint

import mpre.misc.bytecodedis
from mpre.errors import CorruptPickleError

if "win" in sys.platform:
    timer_function = time.clock
else:
    timer_function = time.time

import pickle
import hmac
import hashlib

key = ''.join(chr(x) for x in xrange(256))#os.urandom(512)

def authenticated_dump(py_object, key, _file=None,  hash_algorithm=hashlib.sha512):
    bytestream = pickle.dumps(py_object)
    result = hmac.HMAC(key, bytestream, hash_algorithm).hexdigest() + bytestream
    if _file:
        _file.write(result)
    else:
        return result

def authenticated_load(bytestream, key, hash_algorithm=hashlib.sha512):
    mac_size = hash_algorithm().digestsize * 2
    try:
        pickled_object = bytestream[mac_size:]
    except TypeError:
        bytestream = bytestream.read()
        pickled_object = bytestream[mac_size:]
    valid = hmac.compare_digest(bytestream[:mac_size], 
                                hmac.HMAC(key, pickled_object, hash_algorithm).hexdigest())
    if valid:
        return pickle.loads(pickled_object)
    else:
        raise CorruptPickleError("Message authentication code mismatch\n\n" + mac)
                                 
def load(attributes=None, _file=None):
    """ usage: load([attributes], [_file]) => restored_instance
    
        Loads state preserved by the save method. Loads an instance from either
        a bytestream or file, as returned by the save method..
        
        To customize the behavior of an object after it has been loaded, one should
        extend the on_load method.""" 
    if _file:
        assert not attributes
        attributes = _file.read()    
        
    attributes = authenticated_load(attributes, ''.join(chr(x) for x in xrange(256)))   
    saved_objects = attributes["objects"]
    objects = attributes["objects"] = {}
    for instance_type, saved_instances in saved_objects.items():            
        objects[instance_type] = set([load(instance) for instance in
                                      saved_instances])

    if "_required_modules" in attributes:
        _required_modules = []
        incomplete_modules = attributes["_required_modules"]
        module_sources = dict((module_name, source) for module_name, source, none in 
                              incomplete_modules)

        for module_name, source, none in incomplete_modules[:-1]:
            module = create_module(module_name, source)
            _required_modules.append((module_name, source, module))
        
        class_name = attributes.pop("_class")
        self_class = getattr(module, class_name)
        attributes["_required_modules"] = _required_modules        
    else:
        module_name, class_name = attributes["_required_module"]
        module = importlib.import_module(module_name)
        self_class = getattr(module, class_name)            
    self = self_class.__new__(self_class)
    
    attribute_modifier = attributes.pop("_attribute_type")
    for key, value in attributes.items():
        modifier = attribute_modifier.get(key, '')
        if modifier == "reference":
            attributes[key] = self.environment.Component_Resolve[value]
        elif modifier == "save":
            attributes[key] = load(pickle.loads(value))
            
    self.on_load(attributes)
    self.alert("Loaded", level='v')
    return self  
        
def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)
    new_base_size = len(new_base)
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
    decimal_value = 0    
    new_value = []
    
    for power, value_representation in enumerate(reversed(old_value)):
        decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
                            
    if decimal_value == 0:
        new_value = [new_base[0]]
    else:
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value.append(new_base[digit])

    return ''.join(str(item) for item in reversed(new_value))
                
def resolve_string(string):
    """Given an attribute string of ...x.y.z, import ...x.y and return z"""
    module_name = string.split(".")   
    class_name = module_name.pop(-1)
    module_name = '.'.join(module_name)
    if not module_name:
        module_name = "__main__"
    
    _from = sys.modules[module_name] if module_name in sys.modules\
            else importlib.import_module(module_name)
    return getattr(_from, class_name)

    
def shell(command, shell=False):
    """ usage: shell('command string --with args', 
                     [shell=False]) = > sys.stdout.output from executed command
                    
        Launches a process on the physical machine via the operating 
        system shell. The shell and available commands are OS dependent.
        
        Regarding the shell argument; from the python docs on subprocess.Popen:
            "The shell argument (which defaults to False) specifies whether to use the shell as the program to execute. If shell is True, it is recommended to pass args as a string rather than as a sequence."
            
        and also:        
            "Executing shell commands that incorporate unsanitized input from an untrusted source makes a program vulnerable to shell injection, a serious security flaw which can result in arbitrary command execution. For this reason, the use of shell=True is strongly discouraged in cases where the command string is constructed from external input" """        
    process = subprocess.Popen(command.split(), shell=shell)
    return process.communicate()[0]
    
def function_header(function):
    """usage: function_header(function) => "(arg1, default_arg=True, keyword=True...)"
    
       Given a function, return a string of it's signature."""
    try:
        code = function.func_code
    except AttributeError:
        print function
        
    arguments = inspect.getargs(code)
    _arguments = ', '.join(arguments.args )
    if arguments.varargs:
        _arguments += ", *" + arguments.varargs
    if arguments.keywords:
        _arguments += ", **" + arguments.keywords
    return "(" + _arguments + ")"    
    
def usage(_object):
    if hasattr(_object, "func_name"):
        name = _object.func_name
        arguments = function_header(_object)
        return_type = ''#mpre.misc.bytecodedis.get_return_type(_object)
    elif hasattr(_object, "func_code"):
        name = _object.__name__
        arguments = function_header(_object)
        return_type = ''
    elif hasattr(_object, "defaults") and isinstance(_object.defaults, dict):
        name = _object.__name__ if isinstance(_object, type) else type(_object).__name__
        spacing = ''
        arguments = '({'
        for attribute, value in _object.defaults.items():
            arguments += spacing + attribute + " : " + str(value)
            spacing = '\n' + (len(name) + len("usage: ({")) * " "
        arguments += "})"    
        return_type = " => {}".format(name)
    elif _object.__class__.__name__ == "Runtime_Decorator":
        name = _object.function.__name__
        arguments = function_header(_object.function)
        return_type = ''
    elif hasattr(_object, "__call__"):
        name = _object.__name__ if isinstance(_object, type) else type(_object).__name__
        arguments = function_header(_object.__call__)
        return_type = ''
    else:
        raise ValueError("Unsupported object: {}".format(_object))
    return "usage: {}{}{}".format(name, arguments, return_type)
    
def documentation(_object):
    new_section = "{}\n==============\n\n"
    new_subsection = "{}\n--------------\n\n"
    new_function = "- **{}"
    if isinstance(_object, types.ModuleType):        
        module_name = _object.__name__
        docstring = new_section.format(module_name)
        docstring += _object.__doc__ if _object.__doc__ is not None else ''
        
        for attribute in (attribute for attribute in dir(_object) if "_" != attribute[0]):
            value = getattr(_object, attribute)
            if isinstance(value, type) or callable(value) and "built-in" not in str(value):
                docs = documentation(value)
                if docs:
                    docstring += "\n\n" + docs
            
    elif isinstance(_object, type):
        class_name = _object.__name__
        docstring = new_subsection.format(class_name)
        docs = _object.__dict__["__doc__"]
        if docs.__class__.__name__ == "Docstring":
            docs = _object.__doc    
        elif docs is None:
            docs = "No documentation available"
        docstring += docs.replace("\n", "\n\t\t") + "\n"
        
        for attribute in (attribute for attribute in dir(_object) if "_" != attribute[0]):
            value = getattr(_object, attribute)
            if hasattr(value, "function"):
                docs = documentation(value.function)
                docstring += "\n\n" + docs
            elif hasattr(value, "im_func"):
                docs = documentation(value)           
                docstring += "\n\n" + docs
                
    elif callable(_object):
        try:
            function_name = _object.__name__
        except AttributeError:
            docstring = ''
        else:
            #docstring = new_function.format(function_name)
            docstring = new_function.format(usage(_object)[7:]) + ":"
            docstring += "\n\n\t\t"
            docstring += (_object.__doc__ if _object.__doc__ is not None else 
                          "No documentation available").replace("\n", "\n\t\t") + "\n"
            #docstring += "\n\n\t\t" + ge
            #docstring += method_header + ":\n\n\t\t  " + function_docstring.replace("\n", "\n\t\t ") + "\n"
    elif _object.__class__.__name__ == "Runtime_Decorator":
        docstring = documentation(_object.function)
        
    return docstring

    
class Latency(object):
    """ usage: Latency([name="component_name"], 
                       [average_size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()"""
                
    def __init__(self, name=None, size=20):
        super(Latency, self).__init__()
        self.name = name
        self.latency = 0.0
        self.now = timer_function()
        self.max = 0.0
        self.average = Average(size=size)
        self._position = 0

    def update(self):
        """ usage: latency.update()
        
            notes the current time and adds it to the average time."""
        self._position += 1
        time_before = self.time_before = self.now
        now = self.now = timer_function()
        latency = now - time_before
        self.average.add(latency)
        if (self._position == 20 or latency > self.max):
            self.max = latency
            self._position = 0
        self.latency = latency

    def display(self, mode="sys.stdin"):
        """ usage: latency.display([mode='sys.stdin'])
        
            Writes latency information via either sys.stdin.write or print.
            Information includes the latency average, meta average, and max value""" 
        if "print" in mode.lower():
            print "%s Latency: %0.6f, Average: %0.6f, Max: %0.6f" % \
            (self.name, self.latency, self.average.average, self.max)
        else:
            sys.stdout.write("\b"*120)
            sys.stdout.write("%s Latency: %0.6f, Average: %0.6f, Max: %0.6f" % \
            (self.name, self.latency, self.average.average, self.max))


class Average(object):
    """ usage: Average([name=''], [size=20], 
                       [values=tuple()], [meta_average=False]) => average_object
                       
        Average objects keep a running average via the add method.
        The size option specifies the maximum number of samples. When
        this limit is reached, additional samples will result in the
        oldest sample being removed.
        
        values may be used to seed the average.
        
        The meta_average boolean flag is used to determine whether or not
        to keep an average of the average - This is implemented by an
        additional Average object."""
        
    def _get_meta_average(self):
        average = self._meta_average.average
        if not average:
            average = self.average
        return average
    meta_average = property(_get_meta_average)

    def _get_range(self):
        values = self.values
        return (min(values), self.average, max(values))
    range = property(_get_range)
        
    def __init__(self, name='', size=20, values=tuple(), meta_average=True):
        value = meta_average
        if meta_average:
            value = Average("{0} meta-average".format(name), 30, meta_average=False)
        self._meta_average = value

        self.name = name
        self.values = collections.deque(values, size)
        self.max_size = size
        self.size = float(len(self.values))
        if self.size:
            self.average = sum(self.values) / self.size
        else:
            self.average = 0
        self.add = self.partial_add

    def partial_add(self, value):
        self.size += 1
        self.values.append(value)
        self.average = sum(self.values) / self.size
        if self.size == self.max_size:
            self.add = self.full_add

    def full_add(self, value):
        old_value = self.values[0]
        adjustment = (value - old_value) / self.size
        self.values.append(value)
        self.average += adjustment
        if self._meta_average:
            self._meta_average.add(self.average)

                   
class LRU_Cache(object):
    """A dictionary with a max size that keeps track of
       key usage and handles key eviction. 
       
       currently completely untested"""
    def __init__(self, size=50, seed=None):
        if seed:
            assert len(seed.keys()) <= size
        else:
            seed = dict()
        seed = seed if seed else dict()
        keys = seed.keys()
        assert len(keys) <= size
        
        deque = self.deque = collections.deque(maxlen=size)
        deque.extend(keys)
        
        # testing for x in ... is significantly faster with a set
        self.contains = set(keys)
        self.size = size
        
        # change implementations once cache is full
        self.add = self._add
        
        # when no entry has been evicted (cache is not full or entry was
        # already in it), return a non hashable object so all keys 
        # (None, False, etc) will remain valid for users.
        self.no_eviction = []
        
    def _add(self, item):
        deque = self.deque
        
        if item in self.contains:
            deque.remove(item)
        else:
            self.contains.add(item)
            
        deque.append(item)
        if len(deque) > self.size:
            # change to a slightly different implementation that
            # doesn't do this check when the cache becomes full
            self.add = self._full_add
        
        return self.no_eviction
        
    def _full_add(self, item):
        deque = self.deque
        contains = self.contains
        
        if item in contains:
            deque.remove(item)
            evicted = self.no_eviction
        else:
            contains.add(item)
            evicted = deque[0]
        deque.append(item)
        return evicted
              
    def __getitem__(self, key):
        evicted = self.tracker.add(key)
        dict = self.dict
        if evicted is not self.no_eviction:
            del dict[evicted]
            self.contains.remove(evicted)
        return dict[key]
        
    def __setitem__(self, key, value):
        self.dict[key] = value
        self.contains.add(key)    
        
class Module_Listing(object):

    def __init__(self, _file):
        super(Module_Listing, self).__init__()
        self.file = _file        

    def from_help(self):
        helper = pydoc.Helper(output=self.file)
        helper("modules")

    def read_file(self):
        file = self.file
        file.seek(0)
        text = file.read()
        return text

    def trim(self, text):
        _file = StringIO(text)
        found = []
        count = 0
        for line in _file.readlines():
            if line.split(" ").count("") > 2:
                found += line.split()

        return ' '.join(found)

    def get_modules(self):
        self.from_help()
        original = self.read_file()
        return self.trim(original)

    def make_file(self, filename):
        with open(filename, 'w') as _file:
            _file.write(self.get_modules())
            _file.flush()        