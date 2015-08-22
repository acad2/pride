""" Stores global objects including instructions and the environment """
import sys
import importers        
compiler = importers.Compiler(preprocessors=(importers.Dollar_Sign_Directive(),))#                                             importers.Name_Enforcer()))
sys.meta_path.insert(0, compiler)

import heapq
import inspect
import mmap
import itertools
import pprint
import pickle
import contextlib
import copy
import types

import mpre.utilities
timer_function = mpre.utilities.timer_function          
    
class Environment(object):
    """ Stores global state for the process. This includes reference 
        reference information, most importantly the objects dictionary. """
    fields = ("objects", "instance_count", "instance_name",
              "instance_number", "parents", "references_to")
              
    def __init__(self):
        super(Environment, self).__init__()
        self.Instructions = []
        for field in self.fields:
            setattr(self, field, {})
                
    def display(self):
        """ Pretty prints environment attributes """
        print "\nInstructions: {}".format([(instruction[0], 
                                           str(instruction[1])) for 
                                           instruction in self.Instructions])
        
        for attribute in self.fields:
            print "\n" + attribute
            pprint.pprint(getattr(self, attribute))
    
    def replace(self, component, new_component):
        """ Replaces the instance component with the specified new_component.
            The new_component will be obtain the replaced components
            instance_name reference. The old component should be garbage
            collected. """
        objects = self.objects
        if isinstance(component, unicode) or isinstance(component, str):
            component = self.objects[component]

        old_component_name = component.instance_name
        
        self.objects[old_component_name] = self.objects.pop(new_component.instance_name, new_component)
        
        self.instance_name[new_component] = self.instance_name.pop(component)
        self.instance_number[new_component] = self.instance_number.pop(component)

        parents = self.parents
        if component in parents:
            parents[new_component] = parents.pop(component)
                
        new_component.instance_name = old_component_name
        references = self.references_to.get(old_component_name, set()).copy()
        
        for referrer in references:
            instance = self.objects[referrer]
            instance.remove(component)
            instance.add(new_component)       
        
    def delete(self, instance):
        """ Deletes an object from the environment. This is called by
            instance.delete. """
        try:
            objects = instance.objects
        except AttributeError: # non base objects have no .objects dictionary
            instance_name = self.instance_name[instance]
            parent = self.objects[self.parents[instance]]
            parent.objects[instance.__class__.__name__].remove(instance)          
        else:
            instance_name = instance.instance_name
            if objects:
                for children in objects.values():
                    [child.delete() for child in list(children)] 
                    
        if instance in self.parents:
            del self.parents[instance]  
        
        if instance_name in self.references_to:
            for referrer in list(self.references_to[instance_name]):
                self.objects[referrer].remove(instance)
            del self.references_to[instance_name]            
        del self.objects[instance_name]
        del self.instance_name[instance]
        del self.instance_number[instance]
        
    def add(self, instance):
        """ Adds an instance to the environment. This is done automatically
            for Base objects and for objects instantiated via the create
            method. """
        instance_class = instance.__class__.__name__
        try:
            count = self.instance_count[instance_class]
        except KeyError:
            count = 0       
        instance_name = instance_class + str(count) if count else instance_class
        self.instance_count[instance_class] = count + 1
        
        self.objects[instance_name] = instance
        try:
            self.instance_name[instance] = instance.instance_name = instance_name
            self.instance_number[instance] = instance.instance_number = count
        except AttributeError:
            self.instance_name[instance] = instance_name
            self.instance_number[instance] = count

    def __contains__(self, component):
        if (component in self.objects.keys() or
            component in itertools.chain(self.objects.values())):
            return True
        
    def update(self, environment):    
        """ Updates the fields of the environment. This is currently
            unused and may be deprecated. """
        for instruction in environment.Instructions:
            heapq.heappush(self.Instructions, instruction)

        self.objects.update(objects)
        self.parents.update(environment.parents)
        self.references_to.update(environment.references_to)
        self.instance_number.update(environment.instance_number)
        self.instance_count.update(environment.instance_count)
                                   
        
class Instruction(object):
    """ usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback,
                                                    host_info=(ip, port))
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        host_info may supply an ip address string and port number integer
        to execute the instruction on a remote machine. This requirements
        for this to be a success are:
            
            - The machine must have an instance of metapython running
            - The machine must be accessible via the network
            - The local machine must be registered and logged in to
              the remote machine
            - The local machine may need to be registered and logged in to
              have permission to the use the specific component and method
              in question
            - The local machine ip must not be blacklisted by the remote
              machine.
            - The remote machine may require that the local machine ip
              be in a whitelist to access the method in question.
              
        Other then the security requirements, remote procedure calls require 
        zero config on the part of either host. An object will be accessible
        if it exists on the machine in question.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed if the instruction is being executed
        locally. If the instruction is being executed remotely, this instead
        acts as a flag. If set to a True value, the instruction will be
        placed at the front of the local queue to be sent to the host.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds or sent to the machine in question. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided."""
        
    def __init__(self, component_name, method, *args, **kwargs):
        super(Instruction, self).__init__()
        self.created_at = timer_function()
        self.component_name = component_name
        self.method = method
        self.args = args
        self.kwargs = kwargs
        
    def execute(self, priority=0.0, callback=None,
                host_info=tuple(), transport_protocol="tcp"):
        """ usage: instruction.execute(priority=0.0, callback=None,
                                       host_info=tuple())
        
            Submits an instruction to the processing queue. If being executed
            locally, the instruction will be executed in priority seconds. 
            An optional callback function can be provided if the return value 
            of the instruction is needed.
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If being executed remotely, 
            priority is a high_priority flag where 0 means the instruction will
            be placed at the end of the rpc queue for the remote host in 
            question. If set, the instruction will instead be placed at the 
            beginning of the queue.
            
            Remotely executed instructions have a default callback, which is 
            the appropriate RPC_Requester.alert.
            
            The transport protocol flag is currently unused. Support for
            UDP and other protocols could be implemented and dispatched
            via this flag."""
        if host_info:
            objects["RPC_Handler"].make_request(callback, host_info,
                                                transport_protocol, priority,
                                                self.component_name, 
                                                self.method, self.args,
                                                self.kwargs)
        else:
            heapq.heappush(environment.Instructions, 
                          (timer_function() + priority, self, callback))
        
    def __str__(self):
        return "Instruction({}.{}, {}, {})".format(self.component_name, self.method,
                                                   self.args, self.kwargs)

environment = Environment()
objects = environment.objects

# Things must be done in this order for Alert_Handler to exist inside this file
import mpre.base

class Alert_Handler(mpre.base.Base):
    """ Provides the backend for the base.alert method. The print_level 
        and log_level attributes act as global levels for alerts; 
        print_level and log_level may be specified as command line arguments 
        upon program startup to globally control verbosity/logging. """
    level_map = {0 : 'alert ',
                '' : "stdout ",
                'v' : "notification ",
                'vv' : "verbose notification ",
                'vvv' : "very verbose notification ",
                'vvvv' : "extremely verbose notification "}
                
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"log_level" : '',
                     "print_level" : '',
                     "log_name" : "Alerts.log",
                     "log_is_persistent" : False,
                     "parse_args" : True})
    
    parser_ignore = mpre.base.Base.parser_ignore + ("parse_args", 
                                                    "log_is_persistent", 
                                                    "verbosity")
    exit_on_help = False
    
    def __init__(self, **kwargs):
        super(Alert_Handler, self).__init__(**kwargs)
        self.log = open(self.log_name, 'a+')
                                               
    def _alert(self, message, level):
        if self.print_level is 0 or level <= self.print_level:
            sys.stdout.write(message + "\n")
        if level <= self.log_level:
            severity = self.level_map.get(level, str(level))
            # windows might complain about files in + mode if this isn't done
            self.log.seek(0, 1)
            self.log.write(severity + message + "\n")
            
alert_handler = Alert_Handler()            

host_configuration = {("localhost", 40022) : "localhost"}

class Hosts_Dictionary(mpre.base.Wrapper):
    
    wrapped_object_name = "_hosts"
    
    def __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", {})
        super(Hosts_Dictionary, self).__init__(**kwargs)        
        
    def __getitem__(self, host_key):
        if host_key not in self._hosts:
            username = host_configuration[host_key]
            #self._hosts[host_key] = None # prevents recursion
            self._hosts[host_key] = self.create("mpre.rpc.Host", 
                                                host_info=host_key,
                                                username=username)
        return self._hosts[host_key]
        
    def __setitem__(self, host_key, value):
        self._hosts[host_key] = value
        
hosts = Hosts_Dictionary()        