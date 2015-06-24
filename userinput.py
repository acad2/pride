import functools
import sys
import os
import threading

import mpre
import mpre.vmlibrary
import mpre.utilities
objects = mpre.objects

try:
    from msvcrt import getwch, kbhit
    input_waiting = kbhit
except:
    import select
    def input_waiting():
        return select.select([sys.stdin], [], [], 0.0)[0]
      
def get_user_input(prompt):
    sys.__stdout__.write(prompt)
    sys.__stdout__.flush()
    return raw_input()
    
def get_selection(prompt, answers):
    selection = None
    while selection is None:
        selection = get_user_input(prompt)
        if answers == bool:
            selection = is_affirmative(selection)
        else:
            selection = None if selection not in answers else selection
    return selection            
    
def is_affirmative(input):
    if not input:
        return None
    lowered = input.lower()
    y_location = lowered.find('y')
    n_location = lowered.find('n')
    if y_location != -1:
        if n_location != -1:
            is_positive = True if y_location < n_location else False
        else:
            is_positive = True
    elif n_location != -1:
        is_positive = False       
    for affirmative in ("affirmative", "true"):            
        if affirmative in input:                
            is_positive = True
            break    
    return is_positive

class User_Input(mpre.vmlibrary.Process):
    """ Captures user input and provides the input to any listening component"""
    defaults = mpre.vmlibrary.Process.defaults.copy()
    defaults.update({"thread_started" : False,
                     "input" : ''})
                     
    def __init__(self, **kwargs):
        self.listeners = []
        super(User_Input, self).__init__(**kwargs)       
        self.thread = threading.Thread(target=self.read_input)        
        
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
                objects[listener].handle_keystrokes(self.input)
                
            self.input = ''
                
    def __getstate__(self):
        attributes = super(User_Input, self).__getstate__()
        del attributes["thread"]
        return attributes
    
    def on_load(self, attributes):
        super(User_Input, self).on_load(attributes)
        self.thread = threading.Thread(target=self.read_input)
        self.thread_started = False
        self.input = ''
        
    def add_listener(self, sender):
        """ Adds a component to listeners. objects added this way must support a    
            handle_keystrokes method"""
        self.listeners.append(sender)
        
    def remove_listener(self, sender, argument):
        self.listeners.remove(sender)
        
    def read_input(self):        
        self.input = sys.stdin.readline()
        self.thread = threading.Thread(target=self.read_input)
        self.thread_started = False
        
        
class Keyword_Handler(mpre.base.Base):
    """ usage: objects["Keyword_Handler"].add_keyword('keyword', handler_function)
        
        A command line utility that will examine user entered lines for an
        initial keyword, and call the appropriate handler if the keyword
        was found. For example, typing "$ dir" into the metapython shell
        will run the dir command on the system command line. This behavior
        is extensible via the add_keyword and remove_keyword methods.
        
        Note that keywords must be the first word of the line in order
        for the keyword to be recognized.
        
        The default handler, which is what is used when no keywords were
        found, is the _metapython.Shell. The default handler can be
        set by specifying '' (empty string) as the keyword when calling
        add_keyword."""
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"keyword_handlers" : None,
                     "allow_shell" : True})
                     
    def __init__(self, **kwargs):
        super(Keyword_Handler, self).__init__(**kwargs)
        self.keyword_handlers = self.keyword_handlers or {"$" : functools.partial(mpre.utilities.shell, 
                                                                                  shell=self.allow_shell)}
        mpre.objects["User_Input"].add_listener(self.instance_name)
        
    def add_keyword(self, keyword, handler):
        if not keyword:
            self.default_handler = handler
        else:
            self.keyword_handlers[keyword] = handler
        
    def remove_keyword(self, keyword):
        del self.keyword_handlers[keyword]
        
    def handle_keystrokes(self, line):
        try:
            matched_token = [keyword for keyword in self.keyword_handlers.keys() if
                             line[:len(keyword)] == keyword][0]
        except IndexError:
            self.default_handler(line)
        else:
            self.keyword_handlers[matched_token](line[len(matched_token):])