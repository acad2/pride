import time
import sys

import mpre.base

class Trace_Injector(mpre.base.Base):
    
    def __init__(self, **kwargs):
        super(Trace_Injector, self).__init__(**kwargs)
        sys.settrace(self.tracer)
        
    def on_trace(self, frame, instruction, arg):
        print "Behind the scenes!"
        
    def tracer(self, frame, instruction, arg):
        self.on_trace(frame, instruction, arg)
        return self.tracer
    
