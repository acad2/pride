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
            time = end - start
            return time, result
        


"""class Packed(object):

        def __init__(self, init_function):
                self.init_function = init_function

        def __call__(self, *args, **kwargs):
                instance = self.init_function(*args, **kwargs)
                Display.pack(instance)
                return instance"""

"""class Filter(object):

        def __init__(self, disallowed=None, callback=None):
                self.disallowed_arguments = disallowed
                self.callback = callback

        def __call__(self, function):
                def wrapped_function(*args, **kwargs):
                        new_args = [arg for arg in args]
                        for disallowed in self.disallowed_arguments:
                                print "checking for disallowed argument %s against" % disallowed, args
                                if disallowed in args:
                                        print "found disallowed argument. performing callback"
                                        if hasattr(self, "callback"):
                                                self.callback[0](*self.callback[1:])
                                        else:
                                                new_args.remove(
                        else: # if nothing was disallowed
                                print "all arguments ok"
                                function(*args, **kwargs)
                return wrapped_function"""

                
class Tracer(object):
    
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):        
        tracer = trace.Trace(trace=1)
        return tracer.runfunc(self.function, *args, **kwargs) 
          
  
class Argument_log(object):

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        print "\calling %s with args: %s and kwargs: %s" % (self.function, args, kwargs)
        return self.function(*args, **kwargs)
        print "call to %s complete" % self.function


class EXCEPTIONSAFE(object):

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        try:
            return self.function(*args, **kwargs)
        except:
            print "call to %s failed" % function
         


class ENCODE(object):
    # arbitrary "encoding" decorator. just an example :)
    # currently only functions as a single decorator

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        print "pre encoded args are: ", args
        new_args = []
        for arg in args:

            if type(arg) == int:
                new_args.append(arg*223)
            elif type(arg) == float:
                new_args.append(arg*232.2)
            else:
                new_args.append(arg)
                print "string encoding not implemented"

        args = tuple(new_args)
        print 'post encoded args are:', args
        self.function(*args, **kwargs)

