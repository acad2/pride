import pprint
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

__raw_input = raw_input # so the Interpreter can switch the __builtin__ one to the below
        
def get_user_input(prompt='', must_reply=False):
    """ raw_input function that plays nicely when sys.stdout is swapped.
        If must_reply equals True, then the prompt will be redisplayed
        until a non empty string is returned."""
    if must_reply:
        reply = ''
        while not reply:
            sys.__stdout__.write(prompt)
            sys.__stdout__.flush()        
            reply = __raw_input('')
    else:
        sys.__stdout__.write(prompt)
        sys.__stdout__.flush()       
        reply = __raw_input('')
    return reply
    
def get_permission(prompt):
    """ Displays prompt to the user. Attempts to infer whether or not the supplied
        user input is affirmative or negative via shell.is_affirmative. """
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
        else:
            is_positive = None
    return is_positive

class Command_Line(mpre.vmlibrary.Process):
    """ Captures user input and provides the input to the specified or default program.
    
        Available programs can be modified via the add_program, remove_program,
        set_default_program, and get_program methods."""
    defaults = {"thread_started" : False,
                "write_prompt" : True,
                "prompt" : ">>> ",
                "programs" : None,
                "default_programs" : ("mpre.shell.Shell_Program", 
                                      "mpre.shell.Switch_Program",
                                      "mpre.shell.File_Explorer",
                                      "mpre.programs.register.Registration"),
                "idle_threshold" : 10000}
                     
    def __init__(self, **kwargs):
        self.set_default_program(("Shell", "handle_input"), set_backup=True)
        self._idle = True
        self.screensaver = None
        super(Command_Line, self).__init__(**kwargs)       
        
        self._new_thread()  
        self.programs = self.programs or {}
        
        for program in self.default_programs:
            self.create(program)
        
        priority = self.idle_threshold * self.priority
        mpre.Instruction(self.instance_name, "handle_idle").execute(priority=priority)
        
    def _new_thread(self):
        self.thread = threading.Thread(target=self.read_input) 
        self.thread.daemon = True
        self.thread_started = False
        
    def add_program(self, program_name, callback_info):
        self.programs[program_name] = callback_info
        
    def remove_program(self, program_name):
        del self.programs[program_name]
        
    def set_default_program(self, callback_info, set_backup=False):
        self.default_program = callback_info
        if set_backup:
            self.__default_program = callback_info
            
    def get_program(self, program_name):
        if program_name == "default":
            result = self.default_program
        elif program_name == "__default":
            result = self.__default_program
        else:
            result = self.programs.get(program_name, self.default_program)
        return result
        
    def run(self):
        if input_waiting():
            if self.screensaver is not None:
                mpre.objects[self.screensaver].delete()
                self.screensaver = None           
            if not self.thread_started:
                self._new_thread()    
                self.thread.start()
                self.thread_started = True
                self._idle = False
            
    def set_prompt(self, prompt):
        self.prompt = prompt
        
    def __getstate__(self):
        attributes = super(Command_Line, self).__getstate__()
        del attributes["thread"]
        return attributes
    
    def on_load(self, attributes):
        super(Command_Line, self).on_load(attributes)
        self._new_thread()
        
    def read_input(self):        
        input = sys.stdin.readline()
        self.thread_started = False
        self.alert("Got user input {}".format(input), level='vvv')       
        try:
            program_name, program_input = input.split(' ', 1)
        except ValueError:
            if input.strip() not in self.programs:
                component, method = self.default_program
                program_input = input
            else:
                component, method = self.programs[input]
                program_input = ''                
        else:
            if (program_input != '\n' and program_input.split()[0] in 
               ("+", '-', '*', '%', '/', '//', '**', '=', '==',
                '+=', '-=', '*=', '%=', '/=', '//=', '**=',
                '>>', '<<', '||', '&&', '>>=', '<<=', '||=', '&&=',
                "and", "or", "not")):
                component, method = self.default_program
                program_input = input
            else:
                try:
                    component, method = self.programs[program_name]
                except KeyError:
                    component, method = self.default_program
                    program_input = input  
        mpre.Instruction(component, method, program_input).execute()
        if self.write_prompt:
            sys.stdout.write(self.prompt)
                
    def handle_idle(self):
        if self._idle and not self.screensaver and not self.thread_started:
            self.screensaver = self.create("mpre.shell.Terminal_Screensaver").instance_name
        self._idle = True        
        priority = self.idle_threshold * self.priority
        mpre.Instruction(self.instance_name, "handle_idle").execute(priority=priority)
        
        
class Program(mpre.base.Base):
            
    defaults = {"set_as_default" : False,
                "name" : ''}

    def _get_name(self):
        return self._name or self.instance_name
    def _set_name(self, value):
        self._name = value
    name = property(_get_name, _set_name)
  
    def __init__(self, **kwargs):
        super(Program, self).__init__(**kwargs)
        command_line = objects["Command_Line"]
        
        if self.set_as_default:
            command_line.set_default((self.name, "handle_input"))
        else:
            command_line.add_program(self.name, (self.instance_name, "handle_input"))       
        
    def handle_input(self, input):
        try:
            command, input = input.split(' ', 1)
        except ValueError:
            command = input
            input = ''
        getattr(self, command, self.help)(input)
        
    def help(self, input):
        self.alert("Unrecognized command '{}'".format(input), level=0)
        print self.__doc__
                    
        
class Shell_Program(Program):
            
    defaults = {"use_shell" : True,
                "name" : "shell"}
                     
    def handle_input(self, input):
        mpre.utilities.shell(input, shell=self.use_shell)
        
    
class Switch_Program(Program):
            
    defaults = {"name" : "switch"}
            
    def handle_input(self, input):
        command_line = mpre.objects["Command_Line"]
        if not input:
            input = "__default"
        command_line.set_default_program(command_line.get_program(input.strip()))
        
        
class File_Explorer(Program):
    
    defaults = {"name" : "file_explorer"}
    
    def listdir(self, directory_name='', mode='print'):
        directory_name = directory_name or '.'
        join = os.path.join
        isdir = os.path.isdir        
        contents = {}
        directories = contents["directories"] = []
        files = contents["files"] = []
        
        for filename in os.listdir(directory_name):
            if isdir(join(directory_name, filename)):
                directories.append(filename)
            else:
                files.append(filename)
        if mode == 'print':
            pprint.pprint(contents)
        else:
            return contents
            
            
class Terminal_Screensaver(mpre.vmlibrary.Process):
    
    defaults = {"rate" : 3,
                "priority" : .08,
                "newline_scalar" : 1.5,
                "file_text" : ''}
    
    def __init__(self, **kwargs):
        super(Terminal_Screensaver, self).__init__(**kwargs)
        self._priority = self.priority
            
    def run(self):
        if not self.file_text:
            name, instance = mpre.objects.popitem() # get a random instance
            mpre.objects[name] = instance
            self.file_text = '\n' + name + ':\n' + instance.__doc__
            
        sys.stdout.write(self.file_text[:self.rate])
        if '\n' in self.file_text[:self.rate]:
            self.priority *= self.newline_scalar
        else:
            self.priority = self._priority
            
        self.file_text = self.file_text[self.rate:]            