import sys
import trace
import time
from test import pystone
from functools import wraps
from weakref import ref


seconds, pystones_per_second = pystone.pystones(pystone.LOOPS)


class Pystone_Test(object):
    
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):
        if sys.platform == "win32":
            timer = time.clock
        else:
            timer = time.time
        start_time = timer()
        try:
            result = self.function(*args, **kwargs)
        except:
            end_time = timer()
            time_taken = end_time-start_time
            pystones_result = time_taken/pystones_per_second
            print "%s crashed after %s pystones of work" % (self.function, pystones_result)
            print "local variables: ", locals(), "\n"
            raise
        else:
            end_time = timer()
            time_taken = end_time-start_time
            pystones_result = time_taken/pystones_per_second
            print "%s took %s pystones to perform" % (self.function, pystones_result)
            return result
     
    
class Timed(object):
    
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):
        if sys.platform == "win32":
            timer = time.clock
        else:
            timer = time.time
        start = timer()
        try:
            result = self.function(*args, **kwargs)
        except:
            end = timer()
            print "%s crashed after %ss" % (self.function, end-start)
            print "local variables: ", locals(), "\n"
            raise
        else:
            end = timer()
            run_time = end - start
            return run_time, result
                        
class Tracer(object):
    
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):        
        tracer = trace.Trace(trace=1)
        return tracer.runfunc(self.function, *args, **kwargs) 
          
    
class Dump_Source(Tracer):
    """Tracer decorator that dumps source code to disk instead of writing to sys.stdout."""
    
    def __init__(self, function):
        super(Dump_Source, self).__init__(function)
        
    def __call__(self, *args, **kwargs):
        old_stdout = sys.stdout
        with open("%s_source.txt" % self.function.func_name, "w") as file:
            sys.stdout = file
            super(Dump_Source, self).__call__(*args, **kwargs)
            sys.stdout = old_stdout
            file.close()
            
            
class Argument_log(object):

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        print "\calling %s with args: %s and kwargs: %s" % (self.function, args, kwargs)
        return self.function(*args, **kwargs)
        print "call to %s complete" % self.function           