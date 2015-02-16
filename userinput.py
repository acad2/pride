import sys
from threading import Thread

import mpre.vmlibrary
try:
    from msvcrt import getwch, kbhit
    input_waiting = kbhit
except:
    def input_waiting():
        return select.select([sys.stdin], [], [], 0.0)[0]
        
        
class User_Input(mpre.vmlibrary.Process):

    def __init__(self, **kwargs):
        super(User_Input, self).__init__(**kwargs)
        self.listeners = []
        self.thread = Thread(target=self.read_input)
        
    def run(self):
        if input_waiting():
            self.thread.start()
        
        self.run_instruction.execute()
        
    def add_listener(self, sender, argument):
        self.listeners.append(sender)
        
    def remove_listener(self, sender, argument):
        self.listeners.remove(sender)
        
    def read_input(self):
        line = sys.stdin.readline()
        for listener in self.listeners:
            # for reasons still not understood by me, if sys.stdout
            # is not written to here then at random intervals
            # newline will be written but listener won't receive
            # keystrokes until the next read_input
            sys.stdout.write(" \b")
            self.rpc(listener, "handle_keystrokes " + line)
        
        self.thread = Thread(target=self.read_input)