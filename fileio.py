""" Provides objects for file related tasks """
import sys
import mmap
import os
import StringIO
import pprint
import binascii
import contextlib
import shutil
import platform
import time

import pride    
import pride.vmlibrary as vmlibrary
import pride.base as base
import pride.utilities as utilities
import pride.shell
objects = pride.objects

def ensure_folder_exists(pathname, file_system="disk"):
    """usage: ensure_folder_exists(pathname)
    
       If the named folder does not exist, it is created"""
    path_progress = r''
    for directory in os.path.split(pathname):
        path_progress = os.path.join(path_progress, directory)
        if not os.path.exists(path_progress) or not os.path.isdir(path_progress):
            os.mkdir(path_progress)            
  
def ensure_file_exists(filepath, data=''):
    """usage: ensure_file_exists(filepath, [data=''])
        
        filepath is the absolute or relative path of the file.
        If the file does not exist, it is created
        
        data is optional. if specified, the file will be truncated and 
        the data will written to the file. The file contents will be
        nothing but the specified data"""
    path, _filename = os.path.split(filepath)
    ensure_folder_exists(path)
    with open(filepath, 'a+') as _file:
        if data:
            _file.truncate(0)
            _file.write(data)
            _file.flush()

@contextlib.contextmanager
def current_working_directory(directory_name):
    """ Temporarily sets the current working directory """
    backup = os.getcwd()
    os.chdir(directory_name)
    try:
        yield
    finally:
        os.chdir(backup)
    
@contextlib.contextmanager
def file_contents_swapped(contents, filepath='', _file=None):
    """ Enters a context where the data of the supplied file/filepath are the 
        contents specified in the contents argument."""
    if not _file:
        _file = open(filepath, 'r+b')
    original_contents = _file.read()
    _file.truncate(0)
    _file.seek(0)
    _file.write(contents)
    _file.flush()
    try:
        yield
    finally:
        _file.truncate(0)
        _file.seek(0)
        _file.write(original_contents)
        _file.flush()
        _file.close() 

     
class Cached(object):
    """ A memoization decorator that should work with any method and argument structure"""
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
                                                   
                   
class File_Attributes(pride.base.Adapter):
    
    adaptations = {"protection_bits" : "st_mode", "inode_number" : "st_ino",
                   "number_of_hard_links" : "st_nlink", 
                   "owner_user_id" : "st_uid", "owner_group_id" : "gid",
                   "file_size" : "st_size"}# "last_accessed" : "st_atime",
                  # "last_modified" : "st_mtime", 
                  # "metadata_last_modified" : "st_ctime", # Unix
                  # "date_created" : "st_ctime"} # Windows
                               
    defaults = {"filename" : '',
                "attributes" : ("protection_bits", "inode_number", "device",
                                "number_of_hard_links", "owner_user_id", 
                                "owner_group_id", "file_size", 
                                "last_accessed", "last_modified",
                                "metadata_last_modified", "time_created")} 
    
    if platform.system() == "Linux":
        linux_adaptations = {"blocks_allocated" : "st_blocks", 
                             "filesystem_block_size" : "st_blksize",
                             "device_type" : "st_rdev", 
                             "user_flags" : "st_flags"}  
        adaptations.update(linux_adaptations)
        defaults["attributes"] += tuple(linux_adaptations.keys())
        
    def _get_last_accessed(self):
        return time.asctime(time.localtime(self.wrapped_object.st_atime))
    last_accessed = property(_get_last_accessed)
    
    def _get_last_modified(self):
        return time.asctime(time.localtime(self.wrapped_object.st_mtime))
    last_modified = property(_get_last_modified)
    
    def _get_metadata_last_modified(self):
        assert platform.system() == "Linux"
        return time.asctime(time.localtime(self.wrapped_object.st_ctime))
    metadata_last_modified = property(_get_metadata_last_modified)
    
    def _get_date_created(self):
        assert platform.system() == "Windows"
        return time.asctime(time.localtime(self.wrapped_object.st_ctime))
    date_created = property(_get_date_created)
    
    def __init__(self, **kwargs):
        super(File_Attributes, self).__init__(**kwargs)
        self.wraps(os.stat(self.filename))

        
class File(base.Wrapper):
    """ usage: File(path='', mode='', 
                    file=None, file_type='file', **kwargs) => file
    
        Return a wrapper around a file like object. File objects can be
        saved and loaded. The files contents will be maintained if
        persistent is True, which is the default.
        The wrapped file can be specified by the file argument. 
        If the file argument is not present, a file like object will
        be opened and wrapped. The type may be specified by the file_type
        attribute. The default is a regular file, which will require
        an appropriate path and mode to be specified when initializing. """
        
    defaults = {"file" : None,
                "file_type" : "file",
                "mode" : "",
                "persistent" : True}
    
    def __init__(self, path='', mode='', **kwargs):  
        super(File, self).__init__(**kwargs)
        self.path, self.filename = os.path.split(path)
        if not self.path:
            self.path = os.path.curdir
        
        self.mode = mode or self.mode
        if not self.file:
            if self.file_type == "file":      
                self.file = open(path, self.mode)                
            else:
                self.file = utilities.resolve_string(self.file_type)()             
        self.wraps(self.file)        
        self.properties = self.create("pride.fileio.File_Attributes",
                                      filename=path)
                                      
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.delete()
        return value
        
    def __getitem__(self, slice):
        stop = slice.stop if slice.stop is not None else -1
        start = slice.start if slice.start is not None else 0
        original = self.tell()
        self.seek(start)        
        data = self.file.read(stop)[::slice.step]
        self.seek(original)
        return data
        
    def __setitem__(self, slice, data):
        start = 0 if slice.start is None else slice.start
        if len(data) != slice.stop - start:
            raise IndexError("Slice assignment is wrong size")
        elif slice.step is not None:
            raise ValueError("Slice stepping not supported")
        original = self.tell()
        self.seek(start)
        self.file.write(data)
        self.seek(original)
        
    def __getstate__(self):
        attributes = super(File, self).__getstate__()
        if self.persistent:
            backup_tell = self.tell()
            self.seek(0)
            attributes["_file_data"] = self.read()
            print self.filename, "storing {} bytes of data".format(len(attributes["_file_data"]))
            self.seek(backup_tell)
        else:
            attributes["_file_data"] = ''
        del attributes["wrapped_object"]
        del attributes["file"]
        return attributes
        
    def on_load(self, attributes):
        super(File, self).on_load(attributes)
        if self.file_type == "file":
            self.file = _file = open(self.filename, self.mode)
        else:
            self.file = _file = utilities.resolve_string(self.file_type)()
        self.wraps(_file)
        self.truncate(0)
        self.write(self.__dict__.pop("_file_data"))        
        self.flush()
            
    def delete(self):
        super(File, self).delete()
        self.wrapped_object.close()
                                                
        
class Mmap(object):
    """Usage: mmap [offset] = fileio.Mmap(filename, 
                                          file_position_or_size=0,
                                          blocks=0)
                                 
        Return an mmap.mmap object. Use of this class presumes a
        need for a slice into a potentially large file at an arbitrary
        point without loading the entire file contents. These slices
        are cached so that further requests for the same chunk will return the same mmap.
        
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
            result = mmap.mmap(-1, file_position or 8192 if 'win' in sys.platform else 0)
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
    
    import pride.misc.decoratorlibrary
    Timed = pride.misc.decoratorlibrary
    
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