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
    
    fields = ("Component_Resolve", "Instance_Count", "Instance_Name",
              "Instance_Number", "Component_Memory", "Parents", "References_To",
              "Reference_Location")
              
    def __init__(self):
        super(Environment, self).__init__()
        self.Instructions = []
        for field in self.fields:
            setattr(self, field, {})
                
    def display(self):
        print "\nInstructions: {}".format([(instruction[0], str(instruction[1])) for 
                                           instruction in self.Instructions])
        
        for attribute in ("Component_Resolve", "Instance_Count", "Instance_Name",
                          "Instance_Number", "Component_Memory", "Parents",
                          "References_To", "Reference_Location"):
            print "\n" + attribute
            pprint.pprint(getattr(self, attribute))
    
    def replace(self, component, new_component):
        components = self.Component_Resolve
        if isinstance(component, unicode) or isinstance(component, str):
            component = self.Component_Resolve[component]

        old_component_name = component.instance_name
        
        self.Component_Resolve[old_component_name] = self.Component_Resolve.pop(new_component.instance_name, new_component)
        
        self.Instance_Name[new_component] = self.Instance_Name.pop(component)
        self.Instance_Number[new_component] = self.Instance_Number.pop(component)
        
        memory = self.Component_Memory
        if new_component.instance_name in memory:
            memory[old_component_name] = memory.pop(new_component.instance_name)
        
        parents = self.Parents
        if component in parents:
            parents[new_component] = parents.pop(component)
                
        new_component.instance_name = old_component_name
        references = self.References_To.get(old_component_name, set()).copy()
        
        for referrer in references:
            instance = self.Component_Resolve[referrer]
            instance.remove(component)
            instance.add(new_component)       
        
    def delete(self, instance):
        try:
            for child in itertools.chain(*instance.objects.values()):
                child.delete()
        except AttributeError: # non base objects have no .objects dictionary
            instance_name = self.Instance_Name[instance]
            parent = self.Component_Resolve[self.Parents[instance]]
            parent.objects[instance.__class__.__name__].remove(instance)          
        else:
            instance_name = instance.instance_name
        
        if instance in self.Parents:
            del self.Parents[instance]
        if instance_name in self.Component_Memory:
            self.Component_Memory.pop(instance_name).close()    
        
        if instance_name in self.References_To:
            referrers = [name for name in self.References_To[instance_name]]
            for referrer in referrers:
                self.Component_Resolve[referrer].remove(instance)
            del self.References_To[instance_name]
            
        del self.Component_Resolve[instance_name]
        del self.Instance_Name[instance]
        del self.Instance_Number[instance]
        
    def add(self, instance):
        instance_class = instance.__class__.__name__
        try:
            count = self.Instance_Count[instance_class] + 1
            self.Instance_Count[instance_class] += 1
        except KeyError:
            count = self.Instance_Count[instance_class] = 0
       
        instance_name = instance_class + str(count) if count else instance_class
        self.Component_Resolve[instance_name] = instance
        try:
            self.Instance_Name[instance] = instance.instance_name = instance_name
            self.Instance_Number[instance] = instance.instance_number = count
        except AttributeError:
            self.Instance_Name[instance] = instance_name
            self.Instance_Number[instance] = count
        
        memory_size = getattr(instance, "memory_size", 0)
        if memory_size:
            self.add_memory(instance.instance_name, instance.memory_mode, memory_size)                        
    def add_memory(self, instance_name, memory_mode, memory_size):
        if not memory_mode:
            file_on_disk = open(instance_name, 'a+')
            file_descriptor = file_on_disk.fileno()
        else:
            file_descriptor = -1
        self.Component_Memory[instance_name] = mmap.mmap(file_descriptor, memory_size)     
                            
    def __contains__(self, component):
        if (component in self.Component_Resolve.keys() or
            component in itertools.chain(self.Component_Resolve.values())):
            return True
        
    def update(self, environment):       
        for instruction in environment.Instructions:
            heapq.heappush(self.Instructions, instruction)

        self.Component_Resolve.update(environment.Component_Resolve)
        self.Component_Memory.update(environment.Component_Memory)
        self.Parents.update(environment.Parents)
        self.References_To.update(environment.References_To)
        self.Instance_Number.update(environment.Instance_Number)
        self.Instance_Count.update(environment.Instance_Count)
        
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
        
    def execute(self, priority=0.0, callback=None):
        """ usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed."""
        execute_at = self.execute_at = timer_function() + priority
        heapq.heappush(environment.Instructions, 
                      (execute_at, self, callback))
            
    def __str__(self):
        args = str(getattr(self, "args", ''))
        kwargs = str(getattr(self, "kwargs", ''))
        component = getattr(self, "component_name", '')
        method = getattr(self, "method", '')
        return "{}({}.{}, {}, {})".format(self.__class__.__name__, component, 
                                          method, args, kwargs)  
                                     
environment = Environment()