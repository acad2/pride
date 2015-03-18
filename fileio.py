import mmap
import os
from contextlib import closing

import mpre.vmlibrary as vmlibrary
import mpre.defaults as defaults
import mpre.base as base

def ensure_folder_exists(pathname):
    """usage: ensure_folder_exists(pathname)
    
       If the named folder does not exist, it is created"""
    if not os.path.exists(pathname) or not os.path.isdir(pathname):
        os.mkdir(pathname)
  
def ensure_file_exists(filepath, data=('a', '')):
    """usage: ensure_file_exists(filepath, [data=('a', '')])
        
        filepath is the absolute or relative path of the file.
        If the file does not exist, it is created
        
        data is optional. if specified, data[0] = mode and 
        data[1] = the data to be written
        
        mode should be 'a' or 'w', 'a' is the default. 
        'w' will truncate the file and the only contents
        will be the data supplied in data[1]"""
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        mode, file_data = data
        with open(filepath, mode) as _file:
            if file_data:
                _file.write(file_data)
                _file.flush()
            _file.close()
            
            
class Cached(object):
    cache = {}
    handles = {}
    
    def __init__(self, function):
        self.function = function
        self.cache[function] = {}
        self.handles[function] = {}
        
    def __call__(self, *args, **kwargs):
        cache = self.cache[self.function]
        handles = self.handles[self.function]
        key = str(args) + str(kwargs)
        
        if key in cache:
            result = cache[key]
            handles[key] += 1
        else:
            cache[key] = result = self.function(*args, **kwargs)
            handles[key] = 1
         
        return result
        
    def decrement_handle(self, key):
        function = self.function
        handles = self.handles[function]

        handles[key] -= 1
        if not handles[key]:
            print "deleting cached item", handles[key], key, handles.keys()
            del self.cache[function][key]
        else:
            print "references remaining for", key
        #self.handles[function][key] = handles[key]
                
                
class File(base.Wrapper):
    """usage: file_object = File([filename], [mode], [file])
    
       Creates a File object. File objects are pickleable and
       support the reactor interface for reading/writing to the
       underlying wrapped file."""
        
    def __init__(self, filename='', mode='', file=None, **kwargs):           
        kwargs.setdefault("wrapped_object", (file if file else 
                                             open(filename, mode)))
        print self, "pre super", filename
        super(File, self).__init__(**kwargs)
        print self, "post super", filename
        self.filename = filename
        self.mode = mode
        
    def handle_write(self, sender, packet):
        self.wrapped_object.write(packet)
        
    def handle_read(self, sender, packet):
        seek, byte_count = packet.split(" ", 1)
        self.wrapped_object.seek(seek)
        return "handle_write " + self.file.read(byte_count)
        
    def __getstate__(self):
        return self.filename, self.mode
        
    def __setstate__(self, state):
        self.__init__(*state)
        return self
        
        
class Mmap(object):
    """Usage: mmap [offset] = fileio.Mmap(filename, 
                                          file_position_or_size=0,
                                          blocks=0)
                                 
        Return an mmap.mmap object. Use of this class presumes a
        need for a slice into a potentially large file at an arbitrary
        point without loading the entire file contents. These slices
        are cached, and the size of the cache may be altered.
        
            - if filename is -1 (a chunk of anonymous memory), then no 
              offset is returned. the second argument is interpreted
              as the desired size of the chunk of memory.
            - if filename is specified, the second argument is
              interpreted as the index into the file the slice
              should be opened to.
            
            The default value for the second argument is 0, which will
            open a slice at the beginning of the specified file
            
            - the blocks argument may be specified to request the
              mapping to be of size (blocks * mmap.ALLOCATIONGRANULARITY)
            - this argument has no effect when used with -1 for the filename
            
            """    
    def __new__(cls, filename, file_position=0, blocks=0):
        if filename is -1:
            result = mmap.mmap(-1, file_position)
        else:
            result = Mmap.new_mmap(filename, file_position, blocks)
        return result
        
    @Cached
    def new_mmap(filename, file_position, blocks):
        file_size = os.path.getsize(filename)
        if file_position >= file_size or file_position < 0:
            raise ValueError             
        
        chunk_size = mmap.ALLOCATIONGRANULARITY
        chunk_number, data_offset = divmod(file_position, chunk_size)
        #blocks = min(self.max_blocks_per_mmap, blocks)
                                           
        # calculate the data's displacement + offset into file
        request_size = file_size if file_size <= chunk_size else chunk_size
        request_size = blocks * chunk_size if blocks else request_size
        
        if file_size - file_position < request_size:
            length = file_size - chunk_number * chunk_size
            data_offset = file_position - chunk_number * chunk_size
        else:
            length = request_size
                     
        with open(filename, 'rb') as file_on_disk:
            file_number = file_on_disk.fileno()
        
        args = (file_number, length)        
        kwargs = {"access" : mmap.ACCESS_READ,
                  "offset" : chunk_number * chunk_size}
        
        memory_map = mmap.mmap(*args, **kwargs)
                
        return memory_map, data_offset

    
if __name__ == "__main__":
    def test_case1(filename, iterations=1000):
        for x in xrange(iterations):
            f = open(filename, 'rb')
            f.close()
    
    def test_case2(filename, iterations=1000):
        for x in xrange(iterations):
            f = File(filename, 'rb')
    
    from mpre.misc.decoratorlibrary import Timed
    
    time = Timed(test_case1)("demofile.exe")
    time2 = Timed(test_case2)("demofile.exe")
    print "open: ", time
    print "Cache:", time2
    
    """def test_case(filename, file_position, iterations=100):
        for x in xrange(iterations):
            m, offset = Mmap(filename, file_position)
            
        print "opened at: ", file_position
        print "Data offset into block: ", offset
        print ord(file_data[file_position]), ord(m[offset])
        assert file_data[file_position] == m[offset] 
        
    m, offset = Mmap("demofile.exe", 22892790) 
    demofile = "demofile.exe"
    _file = File(demofile, 'rb')
    file_data = _file.read()
    file_size = len(file_data)
    print
    print "file size: ", file_size
    print
    
    for file_position in (22892790, 0, file_size-1):
        print "testing", file_position
        test_case(demofile, file_position, iterations=2)"""
        
    """for x in xrange(100):
        m, offset = io_manager.load_mmap("newrecording.wav", 2913000)
    for y in xrange(100):
        m2, offset2 = io_manager.load_mmap("testrecording.wav", 3113000)
    
    for x in xrange(10):
        io_manager.load_mmap("newrecording.wav", 3112997)"""