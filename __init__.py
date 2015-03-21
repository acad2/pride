import heapq
import mmap

class Environment(object):
    
    def __init__(self):
        super(Environment, self).__init__()
        self.Instructions = []
        self.Component_Resolve = {}
        self.Component_Memory = {}        
        self.Parents = {}
        self.References_To = {}
    
    def __getstate__(self):
        # mmaps are not pickle-able, but strings are.
        # return a dictionary of component:memory_contents pairs
        # which is pickle-able instead of Component_Memory, which is not
        return (self.Instructions, 
                self.Component_Resolve,
                (dict((owner, memory_chunk[:]) for 
                       owner, memory_chunk in
                       self.Component_Memory.items())),
                self.Parents,
                self.References_To)
        
    def __setstate__(self, state):   
        (self.Instructions, 
         self.Component_Resolve,
         self.Component_Memory,
         self.Parents,
         self.References_To) = state

        component_memory = self.Component_Memory
        component_resolve = self.Component_Resolve
        for component_name, stored_memory in component_memory.items():
            component = component_resolve[component_name]
            memory = mmap.mmap(-1, component.memory_size)
            memory[:len(stored_memory)] = stored_memory
            component_memory[component_name] = memory
        
        return self
    
    def update(self, environment):       
        for instruction in environment.Instructions:
            heapq.heappush(self.Instructions, instruction)

        self.Component_Resolve.update(environment.Component_Resolve)
        self.Component_Memory.update(environment.Component_Memory)
        self.Parents.update(environment.Parents)
        self.References_To.update(environment.References_To)
        
    def modify(self, container_name, item, method="add_key"):
        container = getattr(self, container_name)
        if method == "add_key":
            key, value = item
            container[key] = value
        elif method == "remove_item":
            del container[item]
        else:
            getattr(container, method)(item)
            
environment = Environment()    