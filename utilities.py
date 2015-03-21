#   mpf.utilities - shell commands, latency measurement,
#                    documentation, running average
#
#    Copyright (C) 2014  Ella Rose
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import time
import inspect
import subprocess
import collections
import importlib

if "win" in sys.platform:
    timer_function = time.clock
else:
    timer_function = time.time

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
    
    
class Latency(object):
    """ usage: Latency([name="component_name"], 
                       [average_size=20]) => latency_object
                       
        Latency objects possess a latency attribute that marks
        the average time between calls to latency.update()"""
                
    def __init__(self, name=None, average_size=20):
        super(Latency, self).__init__()
        self.name = name
        self.latency = 0.0
        self.now = timer_function()
        self.max = 0.0
        self.average = Average(size=average_size)
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
        if "print" in mode:
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

        
def function_header(function, mode="signature"):
    """usage: function_header(function, 
                             [mode]) => "(arg1, default_arg=True, keyword=True...)"
    
    Given a function, return it's signature. mode can be specified as insertable
    to use string format insertions instead of argument names"""
    spec = args, varargs, keyword_args, default_args = inspect.getargspec(function)   
    
    header_size = ", ".join("{}" for x in range(len(args)))                
    header_args = [arg for arg in args]
    
    if default_args: 
        new_args = []
        for arg in default_args:
            if isinstance(arg, str):
                new_arg = repr(arg)
            else:
                new_arg = arg
            new_args.append(new_arg)
        default_args = new_args
        non_defaults = len(args) - len(default_args)
        len(default_args)
        header_args = header_args[:non_defaults] + ["{}={}".format(arg_name, default_args[index]) for index, arg_name in enumerate(header_args[non_defaults:])]
        
    if varargs:
        header_size += ", *{}"
        header_args.append(varargs)    
    
    if keyword_args: 
        insert = "**{}" if mode == "signature" else "**{}"
        header_size += ", " + insert
        header_args.append(keyword_args)
     #   print header_size
        
    answer = inserts = "({})".format(header_size)
    
    if mode == "signature":
        answer = inserts.format(*header_args)
    
    return answer
    
    
def documentation(instance):
    """ usage: documentation(object) => augmented_documentation_string
    
        Given a python object, attempt to introspect any useful information
        and include it appended to the objects docstring."""
        
    if isinstance(instance, type):
        _class = instance
    else:
        _class = instance.__class__
    
    options_text = 'Default values for newly created instances:\n\n'
    try: # gather the default attribute names and values (base objects only)
        options = ""
        for key, value in _class.defaults.items():
            options += "- {0: <25}{1}\n".format(key, value)
        if not options:
            options_text = "\nNo defaults are assigned to new instances\n"
        else:
            options_text += options
    except AttributeError: # does not have defaults
        options_text = "\n\n"
        
    docstring = ""
    class_docstring = getattr(_class, "__doc", '')
    if not class_docstring:
        class_docstring = getattr(_class, "__doc__", '')
    docstring += "\t" + class_docstring.replace("    ", '').replace("\n", "\n\t") + "\n\n" + options_text + "\n"
    beginning = docstring    
        
    docstring = "This object defines the following non-private methods:\n"
    found = False
    for attribute_name in _class.__dict__.keys():
        if "_" != attribute_name[0]:
            attribute = getattr(_class, attribute_name)
            if callable(attribute):
                attribute = getattr(attribute, "function", attribute)
                found = True

                docstring += "\n\n- **" + attribute_name + "**"
                                
                function_docstring = inspect.getdoc(attribute)
                function_docstring = function_docstring if function_docstring else "No documentation available"

                try:
                    method_header = function_header(attribute)
                except:
                    print "Could not find header for", attribute
                    raise SystemExit
                docstring += method_header + ":\n\n\t\t  " + function_docstring.replace("\n", "\n\t\t ") + "\n"
                docstring += "\n"          
                
    if found:
        docstring = beginning + docstring
    else:
        docstring = beginning + "No non-private methods are defined\n"
    try:
        mro = str(_class.__mro__).replace("<", "").replace(">", '')
        
    except AttributeError:
        docstring += "\n No method resolution order detected...\n"
    else:
        docstring += "\nThis objects method resolution order is:\n\n"
        docstring += mro + "\n"
    return docstring


class Updater(object):

    def __init__(self):
        super(Updater, self).__init__()

    def live_update(self, component_name, source):
        """Updates base component component_name with a class specified in source.
        
        outdated and needs rewrite"""
        raise NotImplementedError
