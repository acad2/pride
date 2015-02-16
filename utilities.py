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

if "win" in sys.platform:
    timer_function = time.clock
else:
    timer_function = time.time

def shell(command, shell=False):
    process = subprocess.Popen(command.split(), shell=shell)
    return process.communicate()[0]

def ensure_folder_exists(pathname):
    if not os.path.exists(pathname) or not os.path.isdir(pathname):
        os.mkdir(pathname)
  
def ensure_file_exists(filepath, data=''):
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        with open(filepath, 'w') as _file:
            if data:
                _file.write(data)
                _file.flush()
            _file.close()
            
            
class Latency(object):

    def __init__(self, name=None, average_size=20):
        super(Latency, self).__init__()
        self.name = name
        self.latency = 0.0
        self.now = timer_function()
        self.max = 0.0
        self.average = Average(size=average_size)
        self._position = 0

    def update(self):
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
        if "print" in mode:
            print "%s Latency: %0.6f, Average: %0.6f, Max: %0.6f" % \
            (self.name, self.latency, self.average.average, self.max)
        else:
            sys.stdout.write("\b"*120)
            sys.stdout.write("%s Latency: %0.6f, Average: %0.6f, Max: %0.6f" % \
            (self.name, self.latency, self.average.average, self.max))


class Average(object):

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
            self.add = _full_add
        
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
    """function_header(function, [mode]) => "(arg1, default_arg=True, keyword=True...)"
    
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
        """Updates base component component_name with a class specified in source."""
        import mpre.base
        
        new_component_name = source[source.find("class ")+6:source.find("(")] # scoops Name from "class Name(object):"
        code = compile(source, "update", "exec")
        old_component = base.Component_Resolve[component_name]
        exec code in locals(), globals()
        new_component_class = locals()[new_component_name]
        options = {"component" : old_component.parent} # for the Instruction, not actually an instance option
        for attribute_name in dir(old_component):
            if "__" not in attribute_name:
                value = getattr(old_component, attribute_name)
                if not callable(value):
                    options[attribute_name] = value
        new_component = old_component.parent.create(new_component_class, **options)
        base.Component_Resolve[component_name] = new_component
