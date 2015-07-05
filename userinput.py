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
    """ raw_input function that plays nicely when sys.stdout is swapped """
    sys.__stdout__.write(prompt)
    sys.__stdout__.flush()
    return raw_input()

def get_permission(prompt):
    """ Displays prompt to the user. Attempts to infer whether or not the supplied
        user input is affirmative or negative via userinput.is_affirmative. """
    return get_selection(prompt, bool)
    
def get_selection(prompt, answers):
    """ Displays prompt to the user. Only input from the supplied answers iterable
        will be accepted. bool may be specified as answers in order to extract
        a True/False response. """
    selection = None
    while selection is None:
        selection = get_user_input(prompt)
        if answers == bool:
            selection = is_affirmative(selection)
        else:
            selection = None if selection not in answers else selection
    return selection            
    
def is_affirmative(input, affirmative_words=("affirmative", "true")):
    """ Attempt to infer whether the supplied input is affirmative. """
    if not input:
        return None
    lowered = input.lower()    
    for affirmative in affirmative_words:            
        if affirmative in lowered:                
            is_positive = True
            break    
    else:        
        y_location = lowered.find('y')
        n_location = lowered.find('n')
        if y_location != -1:
            if n_location != -1:
                is_positive = True if y_location < n_location else False
            else:
                is_positive = True
        elif n_location != -1:
            is_positive = False       

    return is_positive

class Command_Line(mpre.vmlibrary.Process):
    """ Captures user input and provides the input to the keyword handler."""
    defaults = mpre.vmlibrary.Process.defaults.copy()
    defaults.update({"thread_started" : False,
                     "input" : '',
                     "write_prompt" : True,
                     "prompt" : ">>> "})
                     
    def __init__(self, **kwargs):
        super(Command_Line, self).__init__(**kwargs)       
        self.thread = threading.Thread(target=self.read_input)        
        self.keyword_handler = self.create("mpre.userinput.Keyword_Handler")
        
    def run(self):
        if not self.thread_started and input_waiting():
            self.thread.start()
            self.thread_started = True
            
        if self.input:
            self.keyword_handler.handle_keystrokes(self.input)
            self.input = ''                
            if self.write_prompt:
                sys.stdout.write(self.prompt)
    
    def set_prompt(self, prompt):
        self.prompt = prompt
        
    def __getstate__(self):
        attributes = super(Command_Line, self).__getstate__()
        del attributes["thread"]
        return attributes
    
    def on_load(self, attributes):
        super(Command_Line, self).on_load(attributes)
        self.thread = threading.Thread(target=self.read_input)
        self.thread_started = False
        self.input = ''
        
    def read_input(self):        
        self.input = sys.stdin.readline()
        self.thread = threading.Thread(target=self.read_input)
        self.thread_started = False
        
        
class Keyword_Handler(mpre.base.Base):
    """ usage: objects["Keyword_Handler"].set_keyword('keyword', handler_function)
        
        Examines user entered lines for an initial keyword, and call the 
        appropriate handler if the keyword was found. 
        
        For example, typing "shell dir" into the metapython shell will run the dir 
        command on the system command line. This behavior is extensible via the 
        set_keyword, remove_keyword, and get_handler methods.
        
        Note that keywords must be the first word of the line. 
        
        The default handler, which is what is used when no keywords were
        found, is the _metapython.Shell. 
        
        The default handler can be set by specifying '' (empty string) as 
        the keyword when calling set_keyword. 
        
        Blocking and immediately obtaining user input can be accomplished via
        the userinput.get_x functions"""
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"keyword_handlers" : None,
                     "allow_shell" : True,
                     "default_handler" : None})
                     
    def __init__(self, **kwargs):
        super(Keyword_Handler, self).__init__(**kwargs)
        self.keyword_handlers = (self.keyword_handlers or 
                                 {"shell" : functools.partial(mpre.utilities.shell, 
                                                              shell=self.allow_shell)})
    
    def set_default(self, handler, set_backup=False):
        self.default_handler = handler
        if set_backup:
            self.__default_handler = handler
            
    def set_keyword(self, keyword, handler):
        self.keyword_handlers[keyword] = handler
    
    def get_handler(self, keyword):
        if keyword == "__default":
            result = self.__default_handler
        else:
            result = self.keyword_handlers.get(keyword, self.default_handler)        
        return result
        
    def remove_keyword(self, keyword):
        del self.keyword_handlers[keyword]
        
    def handle_keystrokes(self, line):
        try:
            matched_token = [keyword for keyword in self.keyword_handlers.keys() if
                             line[:len(keyword)] == keyword][0]
        except IndexError:
            if self.default_handler:
                self.default_handler(line)
        else:
            self.keyword_handlers[matched_token](line[len(matched_token):])
            
    def __getstate__(self):
        state = super(Keyword_Handler, self).__getstate__()
        callback = state["default_handler"]
        if callback:
            name = callback.__name__
            module = callback.__module__
            try:
                _class = type(callback.im_self).__name__
            except AttributeError:
                _class = ''
            state["default_handler"] = (module, _class, name)
        return state
        
    def on_load(self, state):
        callback = state["default_handler"]
        if callback:
            module, _class, name = callback
            if _class:
                callback = getattr(objects[_class], name)
            else:
                module = importlib.import_module(module)
                callback = getattr(module, name)
        
        state["default_handler"] = callback    
        super(Keyword_Handler, self).on_load(state)
        
        
class Switch_Keyword(mpre.base.Base):
            
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"name" : "switch"})
    
    def __init__(self, **kwargs):
        super(Switch_Keyword, self).__init__(**kwargs)
        objects["Keyword_Handler"].set_keyword(self.name, self.handle_input)
        
    def handle_input(self, keystrokes):
        keyword, new_handler_keyword = keystrokes.strip().split(" ", 1)
        keyword_handler = objects["Keyword_Handler"]
        if keyword == "default":
            keyword_handler.set_default(keyword_handler.get_handler(new_handler_keyword))
        else:
            keyword_handler.set_keyword(keyword, keyword_handler.get_handler(new_handler_keyword))