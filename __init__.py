import sys
import heapq
import mmap
import itertools
import pprint
import pickle
import contextlib
import copy

import utilities
timer_function = utilities.timer_function  

class Environment(object):
    
    fields = ("objects", "instance_count", "instance_name",
              "instance_number", "parents", "references_to")
              
    def __init__(self):
        super(Environment, self).__init__()
        self.Instructions = []
        for field in self.fields:
            setattr(self, field, {})
                
    def display(self):
        print "\nInstructions: {}".format([(instruction[0], str(instruction[1])) for 
                                           instruction in self.Instructions])
        
        for attribute in ("objects", "instance_count", "instance_name",
                          "instance_number", "parents", "references_to"):
            print "\n" + attribute
            pprint.pprint(getattr(self, attribute))
    
    def replace(self, component, new_component):
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
        instance_class = instance.__class__.__name__
        try:
            self.instance_count[instance_class] = count = self.instance_count[instance_class] + 1
        except KeyError:
            count = self.instance_count[instance_class] = 0
       
        instance_name = instance_class + str(count) if count else instance_class
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
        for instruction in environment.Instructions:
            heapq.heappush(self.Instructions, instruction)

        self.objects.update(objects)
        self.parents.update(environment.parents)
        self.references_to.update(environment.references_to)
        self.instance_number.update(environment.instance_number)
        self.instance_count.update(environment.instance_count)
        
    @contextlib.contextmanager
    def preserved(self):
        backups = [self.Instructions]        
        for field in self.fields:
            backups.append(getattr(self, field).copy())
        try:
            yield
        finally:
            self.Instructions = backups.pop(0)
            for field in self.fields:
                setattr(self, field, backups.pop(0))
                        
    def modify(self, container_name, item, method="add_key"):
        container = getattr(self, container_name)
        if method == "add_key":
            key, value = item
            container[key] = value
        elif method == "remove_item":
            del container[item]
        else:
            getattr(container, method)(item)
                           
        
class Instruction(object):
    """ usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
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
        """ usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed.
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If host_info is supplied
            and callback is None, the results of the instruction will be 
            supplied to RPC_Handler.alert."""
        if host_info:
            objects["RPC_Handler"].make_request(callback, host_info, transport_protocol,
                                                self.component_name, self.method, 
                                                self.args, self.kwargs)
    #    elif not priority:
    #        return (getattr(objects[self.component_name], self.method)
    #                (*self.args, **self.kwargs))
        else:
            execute_at = self.execute_at = timer_function() + priority
            heapq.heappush(environment.Instructions, 
                          (execute_at, self, callback))
    
    #def __getstate__(self):
    #    print "Pickling Instruction", self.component_name, self.method
    #    attributes = self.__dict__
    #    callback = attributes.get("callback")
    #    if callback:
    #        attributes["callback"] = (callback.im_self, callback.__name__)
    #   # print "Pickled instruction", attributes
    #    return attributes
    #    
    #def __setstate__(self, state):
    #    callback = state["callback"]
    #    if callback is not None:
    #        state["callback"] = getattr(objects[callback[0]], callback[1])
    #    super(Instruction, self).__setstate__(state)
        
    def __str__(self):
        args = str(getattr(self, "args", ''))
        kwargs = str(getattr(self, "kwargs", ''))
        component = getattr(self, "component_name", '')
        method = getattr(self, "method", '')
        return "{}({}.{}, {}, {})".format(self.__class__.__name__, component, 
                                          method, args, kwargs)  
                                     
environment = Environment()
objects = environment.objects

# Things must be done in this order for Alert_Handler to exist inside this file
import mpre.base

class Alert_Handler(mpre.base.Base):
    """ Provides the backend for the base.alert method. This component is automatically
        created by the Metapython component. The print_level and log_level attributes act
        as global filters for alerts; print_level and log_level may be specified as 
        command line arguments upon program startup to globally control verbosity/logging."""
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
    
    parser_ignore = mpre.base.Base.parser_ignore + ("parse_args", "log_is_persistent", "verbosity")
    exit_on_help = False
    
    def __init__(self, **kwargs):
        super(Alert_Handler, self).__init__(**kwargs)
        self.log = self.create("mpre.fileio.File", self.log_name, 'a+', persistent=self.log_is_persistent)
                
    def _alert(self, message, level):
        if self.print_level is 0 or level <= self.print_level:
            sys.stdout.write(message + "\n")
        if level <= self.log_level:
            severity = self.level_map.get(level, str(level))
            # windows will complain about a file in + mode if this isn't done sometimes
            self.log.seek(0, 1)
            self.log.write(severity + message + "\n")
            
alert_handler = Alert_Handler()            