import atexit
import os
import contextlib

@contextlib.contextmanager
def file_contents_swapped(contents, filepath=''):
    """ Enters a context where the data of the supplied file/filepath are the 
        contents specified in the contents argument. After exiting the context,
        the contents are replaced.
        
        Note that if a catastrophe like a power outage occurs, pythons context 
        manager may not be enough to restore the original file contents. """
    with open(filepath, "r+b") as _file:
        original_contents = _file.read()
        
        # the context manager isn't enough if CTRL+C happens
        def _in_case_of_failure():
            _file.truncate(0)
            _file.write(original_contents)
            _file.flush()
        atexit.register(_in_case_of_failure)
        
        _file.truncate(0)
        _file.seek(0)
        _file.write(contents)
        _file.flush()
        try:
            yield
        finally:            
            atexit._exithandlers.remove((_in_case_of_failure, tuple(), {}))
            _file.truncate(0)
            _file.seek(0)
            _file.write(original_contents)
            _file.flush()
            _file.close() 
        
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
def backup(_object, *args):    
    backups = dict((attribute, getattr(_object, attribute)) for attribute in args)
    try:
        yield
    finally:
        for attribute, value in backups.items():
            setattr(_object, attribute, value)        

@contextlib.contextmanager        
def inplace_swap(target, new_mutable_sequence):
    backup = target[:]
    target[:] = new_mutable_sequence
    try:
        yield
    finally:
        target[:] = backup
               