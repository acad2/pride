#   mpf.utilities - shell commands, arg parser, latency measurement, 
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

import socket
import sys
import os
import time
import argparse
import inspect
import subprocess
from collections import deque
from StringIO import StringIO

import defaults

def shell(command, shell=False):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, shell=shell)
    return process.communicate()[0]
    
def get_arguments(argument_info, **kwargs):
    arguments = {}
    parser = argparse.ArgumentParser(**kwargs)    
    argument_names = argument_info.keys()
    argument_defaults = argument_info.values()
    
    for index, name in enumerate(argument_names):
        if name[0] == "-":
            short_name = name[1]
            long_name = name[1:]
        else:
            short_name = "-" + name[0]
            long_name = "--" + name
        names = (short_name, long_name)      
        default_value = argument_defaults[index]
        variable_type = type(default_value)
        if variable_type == bool:
            variable_type = int            
        for arg_name in names:
            attribute = long_name.replace("-", '')
            info = {}
            if variable_type is type(None):
                arg_name = attribute
            else:
                info.update({"dest" : attribute, 
                             "default" : default_value,
                             "type" : variable_type})
            arguments[arg_name] = info
            
    for argument_name, options in arguments.items():
        parser.add_argument(argument_name, **options)
    return parser.parse_args()
    
def get_options(argument_info, **kwargs):
    namespace = get_arguments(argument_info, **kwargs)
    options = dict((key, getattr(namespace, key)) for key in namespace.__dict__.keys())
    return options
    
class Latency(object):
    
    def __init__(self, name=None, average_size=20):
        super(Latency, self).__init__()
        self.name = name
        self.latency = 0.0
        self.now = time.clock()
        self.max = 0.0
        self.average = Average(size=average_size)
        self._position = 0

    def update(self):
        self._position += 1
        time_before = self.time_before = self.now
        now = self.now = time.clock()
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
        
    def __init__(self, name='', size=20, values=None):
        if not values:
            values = []
        self.name = name
        self.values = deque(values, size)
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


def documentation(instance):
    if isinstance(instance, type):
        _class = instance
    else:
        _class = instance.__class__
    options_text = '\n Default values for newly created instances:\n'     
    try: # gather the default attribute names and values (base objects only)
        options = ""
        for key, value in _class.defaults.items():
            options += " \t{0:16}\t{1}\n".format(key, value)
        if not options:
            options_text = "\n No defaults are assigned to new instances\n"
        else:
            options_text += options
    except AttributeError: # does not have defaults
        options_text = "\n\n"
    docstring = "%s documentation:\n" % _class.__name__
    class_docstring = getattr(_class, "__doc", '')
    if not class_docstring:
        class_docstring = getattr(_class, "__doc__", '')
    docstring += "\t" + class_docstring + "\n" + options_text + "\n"
    docstring += " This object defines the following public methods:\n"
    count = 0
    found = False
    uses_decorator = False
    for attribute_name in _class.__dict__.keys():
        if "_" != attribute_name[0]:
            attribute = getattr(_class, attribute_name)
            if callable(attribute):
                attribute = getattr(attribute, "function", attribute)
                found = True
                count += 1
                count_string = str(count)        
                docstring += "\n \t"+count_string+". "+ attribute_name + "\n"
                try:
                    argspec = inspect.getargspec(attribute)
                except:
                    continue
                function_docstring = inspect.getdoc(attribute)
                if function_docstring:
                    formatted = ''
                    stringio = StringIO(function_docstring)
                    for line in stringio.readlines():
                        formatted += line + " \t\t"
                    docstring += " \t\tDocstring: " + formatted + "\n\n"
                #docstring += "%s uses the following argument specification:\n"
                if argspec.args:
                    docstring += " \t\tRequired arguments: " + str(argspec.args) + "\n"
                if argspec.defaults:
                    docstring += " \t\tDefault arguments: " + str(argspec.defaults) + "\n"
                if argspec.varargs:
                    docstring += " \t\tVariable positional arguments: " + str(argspec.varargs)+ "\n"
                if argspec.keywords:
                    docstring += " \t\tKeyword arguments: " + str(argspec.keywords) + "\n"""
    if not found:
        docstring += " \tNo public methods defined\n"
    try:
        mro = str(_class.__mro__)
    except AttributeError:
        docstring += "\n No method resolution order detected\n"
    else:
        docstring += "\n This objects method resolution order is:\n \t"
        docstring += mro + "\n"
    return docstring        

    
class Updater(object):
                
    def __init__(self):
        super(Updater, self).__init__()
        
    def live_update(self, component_name, source):
        """Updates base component component_name with a class specified in source."""
        new_component_name = source[source.find("class ")+6:source.find("(")] # scoops Name from "class Name(object):"
        code = compile(source, "update", "exec")
        old_component = base.Component_Resolve[component_name]  
        exec code in locals(), globals()
        new_component_class = locals()[new_component_name]
        options = {"component" : old_component.parent} # for the Event, not actually an instance option
        for attribute_name in dir(old_component):
            if "__" not in attribute_name:
                value = getattr(old_component, attribute_name)
                if not callable(value):
                    options[attribute_name] = value
        new_component = old_component.parent.create(new_component_class, **options)
        base.Component_Resolve[component_name] = new_component
    
        