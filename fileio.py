import sys
import mmap
import os
import pickle
import StringIO
import pprint
import binascii
import contextlib
from contextlib import closing, contextmanager

import mpre    
import mpre.vmlibrary as vmlibrary
import mpre.defaults as defaults
import mpre.base as base
import mpre.utilities as utilities
import mpre.userinput
component = mpre.component

def ensure_folder_exists(pathname, file_system="disk"):
    """usage: ensure_folder_exists(pathname)
    
       If the named folder does not exist, it is created"""
    if not os.path.exists(pathname) or not os.path.isdir(pathname):
        os.mkdir(pathname)
  
def ensure_file_exists(filepath, data=''):
    """usage: ensure_file_exists(filepath, [data=''])
        
        filepath is the absolute or relative path of the file.
        If the file does not exist, it is created
        
        data is optional. if specified, the file will be truncated and 
        the data will written to the file"""
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        with open(filepath, mode) as _file:
            if data:
                _file.write(data)
                _file.flush()
                        
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
                
 
class Directory(base.Base):
    
    defaults = defaults.Directory
    
    def __init__(self, **kwargs):
        super(Directory, self).__init__(**kwargs)
        if not self.path:
            self.delete()
            raise base.ArgumentError("Required argument 'path' not found")
        
        self.file_system, path = os.path.split(self.path)
        self.path, self.filename = os.path.split(path)
        self.parallel_method("File_System", "add", self)        
        
    def delete(self):
        for _file in self.directory[self.filename].values():
            if _file is not self:
                _file.delete()
        super(Directory, self).delete()
                
        
class File(base.Wrapper):
    """ usage: File(filename='', mode='', file=None, file_system="disk", **kwargs) => file
    
        Return a wrapper around a file like object. File objects are pickleable. 
        Upon pickling the files data will be saved and upon loading the data restored. 
        The default is False. The wrapped file can be specified by the file argument. If
        the file argument is not present, the file named in filename will be opened in the
        specified mode."""
        
    defaults = defaults.File
    
    def __init__(self, path='', mode='', **kwargs):  
        super(File, self).__init__(**kwargs)
        if "file_system" not in kwargs:
            try:
                file_system, _path = path.split(os.path.sep, 1)
            except ValueError:
                file_system = self.file_system
                _path = path
            else:
                self.file_system = file_system
                path = _path
                if "File_System" not in component:
                    self.alert("File_System component does not exist", level='v')     
                elif not component["File_System"].exists(file_system, file_type="file_system"):
                    raise IOError("File system '{}' does not exist".format(file_system))
                else:
                    raise RuntimeError("unhandled exception encountered in File __init__")
        self.path, self.filename = os.path.split(path)
        if not self.path:
            self.path = os.path.curdir
        
        self.mode = mode or self.mode
        try:
            mpre.component["File_System"].add(self)
        except KeyError:
            self.alert("File_System does not exist", level='v')
            
        if not self.file:
            if self.file_system == "disk":      
                self.file = open(path, self.mode)                
            else:
                self.file = utilities.resolve_string(self.file_type)()             
        self.wraps(self.file)        
            
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
        backup_tell = self.tell()
        self.seek(0)
        attributes["_file_data"] = self.read()
        self.seek(backup_tell) # in case other objects use it (arguably bad practice anyway)
        del attributes["wrapped_object"]
        del attributes["file"]
        return attributes
        
    def on_load(self, attributes):
        super(File, self).on_load(attributes)
        if self.file_system == "disk":
            self.file = _file = open(self.filename, self.mode)
        else:
            self.file = _file = utilities.resolve_string(self.file_type)()
        self.wraps(_file)
        self.write(self.__dict__.pop("_file_data"))                        
        self.seek(0)
        try:
            self.parallel_method("File_System", "add", self)
        except base.AddError:
            pass
            
    def delete(self):
        super(File, self).delete()
        self.wrapped_object.close()
       #if self.directory and self.filename in self.directory:
        del self.directory
                
        
class Encrypted_File(File):
    """ usage: Encrypted_File(_file, **kwargs) => encrypted_file
               
        Returns an Encrypted_File object. Calls to the write method will be encrypted with
        encrypted_file.key (currently via the mpre.utilities.convert function), and reads will be decrypted using the same key. Currently only supports ascii. Should currently
        be considered as a demonstartion only, please do not depend upon this to keep
        information private.
        
        The key is only valid for as long as the instance exists. In order to preserve
        the key, utilize the save method. The resulting pickle stream can later be
        unpickled and supplied to the load method to recover the original instance with 
        the appropriate key to decrypt the file."""
    
    defaults = defaults.Encrypted_File
        
    def _get_keys(self):
        return (self.key, self.data_pointers)
    keys = property(_get_keys)
    
    def _get_ascii_key(self):
        return ''.join(chr(ordinal) for ordinal in xrange(256))
    asciikey = property(_get_ascii_key)
    
    def __init__(self, filename='', mode='', **kwargs):
        super(Encrypted_File, self).__init__(filename, mode, **kwargs)
        self.key = ''.join(ordinal for ordinal in self.derive_key())
        self.data_pointers = []
        self.slices = {}
        
    def derive_key(self):
        key = []
        while len(key) < 256:
            key.extend(set(os.urandom(128)).difference(key))
        return key
    
    def write(self, data):
       # print "Writing data to encrypted file"#, data
        original_position = position = self.tell()
        slices = self.slices                    
        block_size = self.block_size
        byte_count = 0
        while data:
            _data = self.encrypt(data[:block_size])
            size = len(_data)
            byte_count += size
            current_position = position + size
      #      print "Adding slice: ", position, current_position
            slices[position] = _slice = slice(position, current_position)
            self.data_pointers.append(_slice)
            position = current_position
            data = data[self.block_size:]
            self[_slice] = _data
          #  print "Wrote encrypted slice: ", _data
        #    print "{} bytes left".format(len(data))
        self.seek(original_position + byte_count)
        #self.wrapped_object[self.data_pointers[-1]] = data
    
    def truncate(self, size=None):
        if size is None:
            size = self.tell()
        self.file.truncate(size)
        
        for _slice in self.data_pointers:
            start = _slice.start if _slice.start else 0
            stop = _slice.stop if _slice.stop else 0
            difference = 0
            if size and size >= start and size < stop:
                difference = size - stop
                break
        #print "Data pointers: ", self.data_pointers
        if not size:
            self.data_pointers = []
            self.slices = {}
        else:
            data_pointers = self.data_pointers
            slice_index = data_pointers.index(_slice)                    
            data_pointers = data_pointers[:slice_index]       
            previous_slice = data_pointers[-1]
            data_pointers[-1] = slice(previous_slice.start, previous_slice.stop + difference)
            self.data_pointers = data_pointers if size else []
            self.slices = (dict((_slice.start, _slice) for _slice in self.data_pointers) if 
                        self.data_pointers else {})     
                
    def read(self, size=-1):
      #  print "Reading encrypted data"
        original_position = position = self.tell()
        block_size = self.block_size
        slices = self.slices
        """offset = 0
        if position not in slices:
            print "Using custom offset"
            for _slice in slices.values():
                start = _slice.start if _slice.start is not None else 0
                if position in range(_slice.start, _slice.stop):                    
                    offset = position - start
                    position = start
                    break"""
                    
        result = r''
        data = self[position:size]
        data_size = size = len(data)
        while size:
        #    print "Reading position: ", position
            new_data = self.decrypt(self[slices[position]])
            result += new_data
            byte_count = len(new_data)
            position += byte_count
            size -= byte_count
        self.seek(original_position + data_size)
        return result#[offset:]
        
    def encrypt(self, data):
      #  data = binascii.hexlify(data)
        return utilities.convert(data, self.asciikey, self.key)
        
    def decrypt(self, data):
        return utilities.convert(data, self.key, self.asciikey)
       # return binascii.unhexlify(data)
        

class File_System(base.Base):
            
    defaults = defaults.File_System
    
    def __init__(self, **kwargs):
        super(File_System, self).__init__(**kwargs)
        self.current_working_directory = {}
        self.change_file_system(self.file_systems[0])
        self.file_systems = set(self.file_systems) # no mutables in defaults
        for file_system in self.file_systems:
            setattr(self, file_system, {os.path.curdir : {}})      
            if file_system == "disk":
                self.change_directory(self.join(file_system, os.getcwd()))
            else:
                self.change_directory(self.join(file_system, file_system))
        
    def join(self, path_one, path_two):
        return os.path.sep.join((path_one, path_two))
            
    def listdir(self, path):
        _, is_file = os.path.splitext(path)
        if is_file:
            raise IOError("Path '{}' is not a directory".format(path))
        return self.get_file(path).keys()
    
    def exists(self, path, file_type="file"):
        if file_type == "file_system":
            return path in self.file_systems
        else:
            try:
                file_exists = self.get_file(path)
            except IOError:
                file_exists = False
        return file_exists
    
    def new_file_system(self, file_system):
        setattr(self, file_system, {})
        self.change_directory(self.join(file_system, os.getcwd()))
        self.file_systems.add(file_system)
        
    def add(self, _file):      
       # print "Adding file: ", _file.file_system, _file.path, _file.filename
        directory = self.get_file(self.join(_file.file_system, _file.path))
        if _file.is_directory:
            value = {}
        else:
            value = _file
        directory[_file.filename] = value
        _file.directory = directory
        super(File_System, self).add(_file)
        
    def __str__(self):
        backup = sys.stdout
        log = sys.stdout = StringIO.StringIO()
        for file_system in self.file_systems:
            print "\n{}:".format(file_system)
            _file_system = getattr(self, file_system)
            current_working_directory = os.path.curdir
            removed = _file_system.pop(current_working_directory)
            pprint.pprint(_file_system)
            _file_system[current_working_directory] = removed
        sys.stdout = backup
        log.seek(0)
        return log.read()
        
    def change_directory(self, path):
        file_system, _path = path.split(os.path.sep, 1)
        directory = self.get_file(path)
        self.current_working_directory[file_system] = (path, directory)
        file_system = getattr(self, file_system)
        file_system[os.path.curdir] = directory
        
    def change_file_system(self, file_system):
        if not self.exists(file_system, "file_system"):
            raise ValueError("File system '{}' does not exist".format(file_system))
        self.current_file_system = file_system
        
    def getcwd(self, file_system=''):
        if not file_system:
            file_system = self.current_file_system
        return self.current_working_directory[file_system][0]
        
    def __getitem__(self, path):
        return self.get_file(path)
     
    def __setitem__(self, path, value):
        _path = path.split(os.path.sep)
        self.get_file(os.path.join(*_path[:-1]))[_path[-1]] = value
        
    def get_file(self, path):  
        try:
            file_system, _path = path.split(os.path.sep, 1)
        except ValueError: # os.path.sep was not in path
            if path in self.file_systems:
                return getattr(self, path)
            _path = self.current_working_directory[self.current_file_system][1].get(path)
            if _path:
                return _path
            raise ValueError("Invalid path '{}'".format(path))

        _path, is_file = os.path.splitext(path)
      #  print "Splitting path to acquir lookup chain: ", path
        lookup_chain = path.split(os.path.sep)
        _filename = lookup_chain.pop(-1) if is_file else None
        _file_system = file_system
        try:
            file_system = getattr(self, file_system) 
        except AttributeError:
            raise ValueError("Invalid file_system '{}'".format(_file_system))
       # print "\nGetting file; path:", path
      #  print "Lookup chain: ", lookup_chain
        if not lookup_chain:
            directory = file_system[os.path.curdir]
        else:
            directory = file_system
            for progress, key in enumerate(lookup_chain):
                try:
                #    print "\nLooking for node: ", key
                    directory = directory[key]
                except KeyError:             
                    current_directory = os.path.sep.join(lookup_chain[1:progress + 1])
             #       print "node {} does not exist".format(key)
                    if key == _file_system:
                        directory = file_system
                    elif not is_file:   
                        exists = os.path.exists(current_directory)
                        if not exists:
                            prompt = "Directory '{}' does not exist. Create it? y/n: "
                            permission = mpre.userinput.get_selection(prompt.format(key), bool)
                            if permission:
                                ensure_folder_exists(current_directory)
                                exists = True
                        if exists:
                        #   print "creating node: {}".format(key)
                            directory[key] = {}
                            directory = directory[key]   
                        else:
                            raise IOError("Directory '{}' does not exist".format(key))           
                    else:
                        pprint.pprint(file_system)
                        raise IOError("File '{}' does not exist".format(current_directory))
                
        #pprint.pprint(file_system)        
        result = directory
        if _filename is not None:
            try:
                result = directory[_filename]
            except KeyError:
                file_not_found = "File '{}' does not exist in {} file system"
                raise IOError(file_not_found.format(path, _file_system))
        return result
        
    def remove(self, _file, file_system="disk"):
        super(File_System, self).remove(_file)
        directory = (self.get_file(os.path.join(_file.file_system, _file.path)) if not 
                     _file.directory else _file.directory)
        del directory[_file.filename]
          
        
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
    
    import mpre.misc.decoratorlibrary
    Timed = mpre.misc.decoratorlibrary
    
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