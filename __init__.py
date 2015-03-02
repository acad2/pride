class Environment(object):
    
    def __init__(self):
        super(Environment, self).__init__()
        self.Instructions = []
        self.Parallel_Instructions = []
        self.Component_Resolve = {}
        self.Component_Memory = {}        
        self.Parents = {}
        self.References_To = {}
    
    def __getstate__(self):
        pickleable_memory = {}
        
        for owner, memory_info in self.Component_Memory.items():
            memory_chunk, pointers = memory_info
            pickleable_memory[owner] = (memory_chunk[:], pointers)

        return (self.Instructions, 
                self.Parallel_Instructions,
                self.Component_Resolve,
                pickleable_memory,
                self.Parents,
                self.References_To)
        
    def __setstate__(self, state):
        import mmap
        
        (self.Instructions, 
         self.Parallel_Instructions,
         self.Component_Resolve,
         pickled_memory,
         self.Parents,
         self.References_To) = state

        self.Component_Memory = {}
        for component_name, stored_memory in pickled_memory.items():
            bytes, pointers = stored_memory
            component = self.Component_Resolve[component_name]
            memory = mmap.mmap(-1, component.memory_size)
            memory.write(bytes)
            memory.seek(0)
            self.Component_Memory[component_name] = (memory, pointers)
        
        return self
    
    def update(self, environment):
        import heapq
        
        for instruction in environment.Instructions:
            heapq.heappush(self.Instructions, instruction) 

        self.Parallel_Instructions.extend(environment.Parallel_Instructions)
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