""" Provides objects for file related tasks """
import sys
import mmap
import os
import StringIO
import platform
import time
import datetime
import sqlite3

import pride    
import pride.database
import pride.vmlibrary as vmlibrary
import pride.base as base
import pride.utilities as utilities
import pride.shell
#objects = pride.objects

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
        if self.filename and not self.wrapped_object:
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
        
    defaults = {"file" : None, "file_type" : "file", "mode" : "",
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
                self.properties = self.create("pride.fileio.File_Attributes",
                                              filename=path)              
                self.filesize = self.properties.file_size
            else:
                self.file = resolve_string(self.file_type)()
                self.filesize = 0
            #    self.properties = self.create("pride.filefio.File_Attributes",
            #                                  wrapped_object=self.file, filename=path)
        self.wraps(self.file)      
                                      
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.delete()
        if traceback:
            raise
        return value
    
    def write(self, data):
        self.file.write(data)
        self.filesize += len(data)
        
    def truncate(self, size=None):
        if size is None:
            self.filesize -= self.filesize - self.file.tell()
        else:
            self.filesize -= self.filesize - size
        self.file.truncate(size)
        
    def __getitem__(self, slice):
        original = self.tell()
        try:
            stop = slice.stop if slice.stop is not None else -1
        except AttributeError: 
            if slice < 0:
                slice = self.filesize + slice
            self.seek(slice)
            data = self.read(1)
        else:    
            start = slice.start if slice.start is not None else 0
            stop = stop - start
            if start < 0:
                start = self.filesize + start            
            self.seek(0)
            size = len(self.read())
            self.seek(start)        
            data = self.read(stop)[::slice.step]
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
        del attributes["properties"]
        del attributes["objects"]["File_Attributes"]
        return attributes
        
    def on_load(self, attributes):
        super(File, self).on_load(attributes)
        if self.file_type == "file":
            self.file = _file = open(self.filename, self.mode)
            self.properties = self.create("pride.fileio.File_Attributes", filename=path)             
        else:
            self.file = _file = resolve_string(self.file_type)()
        self.wraps(_file)
        self.truncate(0)
        self.write(self.__dict__.pop("_file_data"))        
        self.flush()
            
    def delete(self):
        super(File, self).delete()
        self.wrapped_object.close()
                                                
    def delete_from_filesystem(self):
        if self.file_type == "file":
            os.remove(self.filename)
            self.delete()
        else:
            raise ValueError("File type '{}' does not exist on file system".format(self.file_type))
        pride.objects["/Python/File_System"].delete_file(self.filename)
                
        
class Database_File(File):
    """ A file that persists in the /Python/File_System when saved or flushed.
        Standard read/write/seek operations take place with a file like object
        of type file_type. Data is manipulated in memory and is only saved to the 
        database when flush or save is called. 
        
        tags may be specified as an iterable of strings describing the 
        contents or purpose of the file. Files in the file system can be
        searched by tag. Tags may be modified whenever required by assigning
        them when creating the file.
        
        The encrypted flag determines whether or not to encrypt file data
        stored in the file system database. Only file data is encrypted, not
        metadata or file name. Data is encrypted using pride.security.encrypt,
        which defaults to AES-GCM with a 16 byte random salt. The encryption
        key is that of the currently logged in User; If no User is logged in,
        files cannot be encrypted or decrypted. The encrypt flag only applies
        to memory saved onto the file system database; The contents of memory
        are not encrypted. """
    defaults = {"_data" : '', "tags" : '', "file_type" : "StringIO.StringIO",
                "encrypted" : False, "indexable" : True}
        
    def __init__(self, filename='', mode='', **kwargs):
        super(Database_File, self).__init__(filename, mode, **kwargs)        
        data, tags = pride.objects["/Python/File_System"]._open_file(self.filename, self.mode, 
                                                                     self.tags, self.indexable)
        filename = {"filename" : self.filename}
        if tags != self.tags:
            for old_tag in set(self.tags).difference(tags):
                self.delete_from(old_tag, where=filename)
        self.tags = self.tags or tags
        if self.encrypted and data:
            data, _filename = pride.objects["/User"].decrypt(data)
            if self.indexable:
                assert _filename == filename["filename"], (_filename, filename["filename"])
            else:                                               
                filename = objects["/Python/File_System"]._hash(filename["filename"])
                assert _filename == filename, (_filename, filename)
                
        self.file.write(data)
        if self.mode[0] != 'a':
            self.file.seek(0)
            
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        if not self.deleted:
            # delete_from_filesystem can be called in the context
            self.save()
            self.delete()        
        if traceback:
            raise
        return value
        
    def flush(self): 
        self.save()
        self.file.flush()

    def close(self):
        self.flush()
        self.delete()
        
    def save(self):
        """ Saves file contents and metadata to /Python-File_System. """
        file = self.file
        backup_position = file.tell()
        file.seek(0)        
        pride.objects["/Python/File_System"].save_file(self.filename, file.read(), 
                                                         self.tags, self.encrypted,
                                                         self.indexable)                                                       
        file.seek(backup_position)
        
    def delete_from_filesystem(self):
        pride.objects["/Python/File_System"].delete_file(self.filename)
        self.delete()
        
        
class File_System(pride.database.Database):
    """ Database object for managing database file objects. """    
    defaults = {"hash_function" : "SHA256", "salt_size" : 16, "database_name" : ''}
    
    verbosity = {"file_modified" : "vv", "file_created" : "vv"}
    
    database_structure = {"Files" : ("filename BLOB PRIMARY KEY", "data BLOB",
                                     "date_created TIMESTAMP", "date_modified TIMESTAMP",
                                     "date_accessed TIMESTAMP", "file_type TEXT",
                                     "tags TEXT"),
                          "Tags" : ("tag TEXT PRIMARY_KEY", )}
     
    primary_key = {"Files" : "filename", "Tags" : "tag"}
    
    def __init__(self, **kwargs):
        super(File_System, self).__init__(**kwargs)
        database_structure = self.database_structure
        for tag in self.query("Tags"):
            tag = tag[0]
            if tag not in database_structure:
                self.create_table(tag, ("filename TEXT PRIMARY_KEY", ))
    
    def _hash(self, filename):
        user = objects["/User"]
        hasher = pride.security.hash_function(self.hash_function)
        assert user.file_system_key, filename
        assert user.salt, filename
        hasher.update(user.file_system_key + user.salt + filename)
        return hasher.finalize()   
                
    def save_file(self, filename, data, tags=tuple(), encrypt=False, indexable=True):
        now = time.time()
        file_info = {}          
        if not indexable: 
            filename = self._hash(filename)                    
            
        if encrypt and data:
            data = objects["/User"].encrypt(data, extra_data=filename)
               
        file_info.update({"date_modified" : now, "date_created" : now, "data" : data, 
                         "file_type" : os.path.splitext(filename)[-1] if indexable else ''})
        if tags:
            file_info["tags"] = ' '.join(tags)
            for tag in tags:
                if tag not in self:
                    self.create_table(tag, ("filename TEXT PRIMARY_KEY", ))
                    self.insert_into("Tags", (tag, ))
                self.insert_into(tag, (filename, ))   
        try:            
            self.insert_into("Files", (filename, data, now, now, now, 
                                       file_info["file_type"], 
                                       file_info.get("tags", '')))
        except sqlite3.IntegrityError:
            self.alert("Updating preexisting file: {}".format(filename), 
                       level=self.verbosity["file_modified"])
            del file_info["date_created"]
            self.update_table("Files", where={"filename" : filename}, arguments=file_info)
        else:
            self.alert("Saving new file: {}".format(filename), 
                       level=self.verbosity["file_created"])
        
    def _open_file(self, filename, mode, tags, indexable):        
        if not indexable:        
            filename = self._hash(filename)
            
        if mode[0] == 'w':
            try:
                self.delete_from("Files", where={"filename" : filename})
            except sqlite3.Error:
                pass
            self.save_file(filename, '', tags)    
        result = self.query("Files", where={"filename" : filename},
                            retrieve_fields=("data", "tags"))        
        if not result and mode[0] == 'r':
            raise IOError("File {} does not exist in {}".format(filename, self.reference))
        return result or ('', '')
        
    def open_file(self, filename, mode):
        return self.create(Database_File, filename, mode)
        
    def delete_file(self, filename):
        self.delete_from("Files", where={"filename" : filename})
        
    def __contains__(self, filename):
        if self.open_file(filename, 'r'):
            return True
        else:
            return False
        
        
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
    
    import pride.decoratrs
    Timed = pride.decoratrs
    
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