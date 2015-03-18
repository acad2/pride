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
         pickled_memory,
         self.Parents,
         self.References_To) = state

        self.Component_Memory = {}
        for component_name in pickled_memory.items():
            bytes = stored_memory
            component = self.Component_Resolve[component_name]
            memory = mmap.mmap(-1, component.memory_size)
            memory.write(stored_memory)
            memory.seek(0)
            self.Component_Memory[component_name] = memory
        
        return self
    
    def update(self, environment):
        import heapq
        
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