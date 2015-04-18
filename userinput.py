import sys
from threading import Thread

import mpre.vmlibrary as vmlibrary
import mpre.defaults as defaults

try:
    from msvcrt import getwch, kbhit
    input_waiting = kbhit
except:
    import select
    def input_waiting():
        return select.select([sys.stdin], [], [], 0.0)[0]
        
        
class User_Input(vmlibrary.Process):

    defaults = defaults.User_Input
    
    def __init__(self, **kwargs):
        self.listeners = []
        super(User_Input, self).__init__(**kwargs)        
        self.thread_started = False
        self.thread = Thread(target=self.read_input)
        self.input = ''
        
    def run(self):
        if not self.thread_started and input_waiting():
            self.thread.start()
            self.thread_started = True
            
        if self.input:
            message = "handle_keystrokes " + self.input
            for listener in self.listeners:
                # for reasons still not understood by me, if sys.stdout
                # is not written to here then at random intervals
                # newline will be written but listener won't receive
                # keystrokes until the next read_input
                sys.stdout.write(" \b")
                self.reaction(listener, message)
            self.input = ''
            
        self.run_instruction.execute(priority=self.priority)
    
    def __getstate__(self):
        attributes = super(User_Input, self).__getstate__()
        del attributes["thread"]
        return attributes
    
    def on_load(self, attributes):
        super(User_Input, self).on_load(attributes)
        self.thread = Thread(target=self.read_input)
        self.thread_started = False
        self.input = ''
        
    def add_listener(self, sender, argument):
        self.listeners.append(sender)
        
    def remove_listener(self, sender, argument):
        self.listeners.remove(sender)
        
    def read_input(self):        
        self.input = sys.stdin.readline()
        self.thread = Thread(target=self.read_input)
        self.thread_started = False