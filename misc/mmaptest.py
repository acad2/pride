import mmap
import os
from contextlib import closing

import mpre.vmlibrary as vmlibrary
import mpre.defaults as defaults
import mpre.base as base



class File(base.Wrapper):
    
    defaults = defaults.Base.copy()
    cache = {}
    open_handles = {}
    
    def __new__(cls, filename, mode='r', **kwargs):
        cache = File.cache
        open_handles = File.open_handles
        
        if filename in cache:
            _file = cache[filename]
            open_handles[filename] += 1
        else:
            print "opening new file"
            _file = cache[filename] = super(File, cls).__new__(cls, filename, mode, **kwargs)
            _file.wraps(open(filename, mode))
            open_handles[filename] = 1           
            
        return _file
        
    def __init__(self, filename, mode='r', **kwargs):        
        super(File, self).__init__(**kwargs)        
        
    def delete(self):
        File.open_handles[self.filename] -= 1
        if not File.open_handles[self.filename]:
            self.close()
        super(File, self).delete()
        
            
class IO_Manager(vmlibrary.Process):
    
    defaults = defaults.Process.copy()
    defaults.update({"max_blocks_per_mmap" : 5,
                     "total_mmap_blocks_allowed" : 50})
                     
    public_methods = ("load_mmap", )
    
    def __init__(self, **kwargs):
        self.mmap_cache = {}
        self.file_cache = {}
        super(IO_Manager, self).__init__(**kwargs)
        self.cache_mmaps = True
        self.cache_files = True
        self.cached_blocks = 0
        
    def load_mmap(self, filename, start_index, blocks=0):
        file_size = os.path.getsize(filename)
        if start_index >= file_size or start_index < 0:
            raise ValueError             
        
        chunk_size = mmap.ALLOCATIONGRANULARITY
        chunk_number, data_offset = divmod(start_index, chunk_size)
        blocks = min(self.max_blocks_per_mmap, blocks)
                       
        try:
            return self.mmap_cache[(filename, chunk_number, blocks)], data_offset         
        except KeyError:
            pass
                    
        # calculate the data's displacement + offset into file
        request_size = file_size if file_size <= chunk_size else chunk_size
        request_size = blocks * chunk_size if blocks else request_size
        
        if file_size - start_index < request_size:
            length = file_size - chunk_number * chunk_size
            data_offset = start_index - chunk_number * chunk_size
        else:
            length = request_size
                     
        file_on_disk = self.create(File, filename, 'rb')
                    
        args = (file_on_disk.fileno(), length)        
        kwargs = {"access" : mmap.ACCESS_READ,
                  "offset" : chunk_number * chunk_size}
        print "opening new mmap"
        memory_map = mmap.mmap(*args, **kwargs)
        
        if self.cache_mmaps:
            self.mmap_cache[(filename, chunk_number, blocks)] = memory_map
            self.cached_blocks += max(blocks, 1)
            
            self.alert("cacheing new mmap. currently {}/{} blocks cached", (self.cached_blocks, self.total_mmap_blocks_allowed), level='v')
            
            if self.cached_blocks > self.total_mmap_blocks_allowed:
                self.alert("making room in cache for new mmap", level='v')
                
                for mapping_info in self.mmap_cache.keys():
                    if self.cached_blocks - mapping_info[2] <= self.total_blocks_allowed:
                        self.mmap_cache.pop(mapping_info)
                        break
                        
        return memory_map, data_offset
        
    def delete(self):
        for _file in self.objects["file"]:
            _file.close()
        for memory_map in self.mmap_cache.values():
            memory_map.close()
        super(IO_Manager, self).delete()
        
        
if __name__ == "__main__":
    io_manager = IO_Manager(auto_start=False)
    
    for x in xrange(100):
        m, offset = io_manager.load_mmap("newrecording.wav", 2913000)
    for y in xrange(100):
        m2, offset2 = io_manager.load_mmap("testrecording.wav", 3113000)
    
    for x in xrange(10):
        io_manager.load_mmap("newrecording.wav", 3112997)