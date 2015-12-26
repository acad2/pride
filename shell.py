import random
import pprint
import sys
import os
import threading

import pride
import pride.vmlibrary
import pride.utilities
import pride._termsize
objects = pride.objects

try:
    from msvcrt import getwch, kbhit
    input_waiting = kbhit
    PLATFORM = "Windows"
except:
    PLATFORM = "POSIX"
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

class Command_Line(pride.vmlibrary.Process):
    """ Captures user input and provides the input to the specified or default program.
    
        Available programs can be modified via the add_program, remove_program,
        set_default_program, and get_program methods."""
    defaults = {"thread_started" : False, "write_prompt" : True,
                "prompt" : ">>> ", "programs" : None,
                "default_programs" : ("pride.shell.Shell_Program", 
                                      "pride.shell.Switch_Program",
                                      "pride.shell.File_Explorer",
                                      "pride.programs.register.Registration"),
                "idle_threshold" : 10000, 
                "screensaver_type" : "pride.shell.CA_Screensaver"}
                     
    def __init__(self, **kwargs):
        self._idle = True
        self.screensaver = None
        super(Command_Line, self).__init__(**kwargs)       
        
        self._new_thread()  
        self.programs = self.programs or {}
        self.set_default_program("python", ("->User->Shell", "handle_input"), set_backup=True)
        
        for program in self.default_programs:
            self.create(program)
        
        priority = self.idle_threshold * self.priority
        pride.Instruction(self.instance_name, "handle_idle").execute(priority=priority)
        
    def _new_thread(self):
        self.thread = threading.Thread(target=self.read_input) 
        self.thread.daemon = True
        self.thread_started = False
        
    def add_program(self, program_name, callback_info):
        self.programs[program_name] = callback_info
        
    def remove_program(self, program_name):
        del self.programs[program_name]
        
    def set_default_program(self, name, callback_info, set_backup=False):
        if name not in self.programs:
            self.programs[name] = callback_info
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
                pride.objects[self.screensaver].delete()
                self.screensaver = None
                self.clear()
                #line_width, line_count = pride._termsize.getTerminalSize()
                sys.stdout.write(sys.stdout_log[:self._position])
               # sys.stdout.write(self.prompt)
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
        pride.Instruction(component, method, program_input).execute()
        if self.write_prompt:
            sys.stdout.write(self.prompt)
                
    def handle_idle(self):
        if self._idle and not self.screensaver and not self.thread_started:
            self._position = sys.stdout_log.tell()
            self.screensaver = self.create(self.screensaver_type).instance_name            
        self._idle = True        
        priority = self.idle_threshold * self.priority
        pride.Instruction(self.instance_name, "handle_idle").execute(priority=priority)
        
    def clear(self):
        if PLATFORM == "Windows":
            command = "CLS"
        else:
            command = "CLEAR"
        os.system(command)
        
        
class Program(pride.base.Base):
            
    defaults = {"set_as_default" : False, "name" : ''}

    def _get_name(self):
        return self._name or self.instance_name
    def _set_name(self, value):
        self._name = value
    name = property(_get_name, _set_name)
  
    def __init__(self, **kwargs):
        super(Program, self).__init__(**kwargs)
        command_line = objects["->User->Command_Line"]
        
        if self.set_as_default:
            command_line.set_default(self.name, (self.instance_name, "handle_input"))
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
            
    defaults = {"use_shell" : True, "name" : "shell"}
                     
    def handle_input(self, input):
        pride.utilities.shell(input, shell=self.use_shell)
        
    
class Switch_Program(Program):
            
    defaults = {"name" : "switch"}
            
    def handle_input(self, input):
        command_line = pride.objects["->User->Command_Line"]
        if not input:
            input = "__default"
        _input = input.strip()
        command_line.set_default_program(_input, command_line.get_program(_input))
        
        
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
            
            
class Terminal_Screensaver(pride.vmlibrary.Process):
    
    defaults = {"rate" : 3, "priority" : .08, "newline_scalar" : 1.5,
                "file_text" : ''}
    
    def __init__(self, **kwargs):
        super(Terminal_Screensaver, self).__init__(**kwargs)
        self._priority = self.priority
            
    def run(self):
        if not self.file_text:
            name, instance = pride.objects.popitem() # get a random instance
            pride.objects[name] = instance
            self.file_text = '\n' + name + ':\n' + instance.__doc__
            
        sys.stdout.write(self.file_text[:self.rate])
        if '\n' in self.file_text[:self.rate]:
            self.priority *= self.newline_scalar
        else:
            self.priority = self._priority
            
        self.file_text = self.file_text[self.rate:]
        
        
class Matrix_Screensaver(Terminal_Screensaver):
    
    defaults = {"priority" : .08}
    
    def __init__(self, **kwargs):
        super(Matrix_Screensaver, self).__init__(**kwargs)
        self.characters = []
        self.width, self.height = pride._termsize.getTerminalSize()
        self.row = None
        for x in xrange(self.height):
            self.characters.append(bytearray(self.width))            
            
    def run(self):
        if not self.row: # pick a new row at random to go down
            row_number = 0
            used_numbers = set()
            while self.characters[0][row_number]:
                row_number = random.randint(0, self.width - 1)
                used_numbers.add(row_number)
                if len(used_numbers) == self.width:
                    self.characters = []
                    for x in xrange(self.height):
                        self.characters.append(bytearray(self.width))
                    break
            self.row = row_number
            self.column = 0
        self.characters[self.column][self.row] = chr(random.randint(0, 255))
        sys.stdout.write(str(self.characters[self.column]))
        sys.stdout.flush()        
        self.column += 1
        if self.column >= self.height:
            self.row = None            
            objects["->User->Command_Line"].clear()
            
            
class CA_Screensaver(Terminal_Screensaver):
                
    defaults = {"storage_size" : 1024}
    
    next_state = {(1, 1, 1) : 1, (1, 1, 0) : 0, (1, 0, 1) : 0, (1, 0, 0) : 1,
                  (0, 1, 1) : 0, (0, 1, 0) : 1, (0, 0, 1) : 1, (0, 0, 0) : 0}
 
    rule_30 = {(1, 1, 1) : 0, (1, 1, 0) : 0, (1, 0, 1) : 0, (1, 0, 0) : 1,
               (0, 1, 1) : 1, (0, 1, 0) : 1, (0, 0, 1) : 1, (0, 0, 0) : 0}
           
    def __init__(self, **kwargs):
        super(CA_Screensaver, self).__init__(**kwargs)
        self.bytearray = bytearray(1024)
        self.bytearray[sum(ord(random._urandom(1)) for x in xrange(4))] = 1
        self._state = CA_Screensaver.rule_30 if random._urandom(1) < 128 else CA_Screensaver.next_state
        
    def run(self):
        _bytearray = self.bytearray
        size = self.storage_size
        new_bytearray = bytearray(size)
        _state = self._state
        for index, byte in enumerate(_bytearray):
            current_state = (_bytearray[index - 1], byte, _bytearray[(index + 1) % size])
            new_bytearray[index] = _state[current_state]
        self.bytearray = new_bytearray
        objects["->User->Command_Line"].clear()
        sys.stdout.write(new_bytearray)            
        
        
class Wave_CAtest(Terminal_Screensaver):
    
    def __init__(self, **kwargs):
        super(Wave_CAtest, self).__init__(**kwargs)
        self.rows = [[(0, 0) for y in xrange(16)] for x in xrange(16)]
        random_coordinate = format(ord(random._urandom(1)), 'b').zfill(8)
        x = int(random_coordinate[:4], 2)
        y = int(random_coordinate[4:], 2)
        self.rows[x][y] = (ord(random._urandom(1)), ord(random._urandom(1)))
        
    def run(self):
        new_rows = [[(0, 0) for y in xrange(16)] for x in xrange(16)]
        
        last_row = False
        for row_index, row in enumerate(self.rows):
            new_row = [(0, 0) for x in range(16)]
            if row_index == 15:
                last_row = True
            for point_index, magnitudes in enumerate(row):
                x_magnitude, y_magnitude = magnitudes
                if point_index == 15:
                    x_magnitude = -x_magnitude  
                if x_magnitude > 0:
                    x_magnitude -= 1
                    new_x_coord = point_index + 1
                elif x_magnitude < 0:
                    x_magnitude += 1
                    new_x_coord = point_index - 1
                else:
                    new_x_coord = point_index
                    
                if last_row:
                    y_magnitude = -y_magnitude
                if y_magnitude > 0:
                    y_magnitude -= 1
                    new_y_coord = row_index + 1
                elif y_magnitude < 0:
                    y_magnitude += 1
                    new_y_coord = row_index - 1
                else:
                    new_y_coord = row_index
                if new_y_coord > 15:
                    new_y_coord = 15
                elif new_y_coord < 0:
                    new_y_coord = 0
                    y_magnitude = -y_magnitude
                if new_x_coord > 15:
                    new_x_coord = 15
                elif new_x_coord < 0:
                    new_x_coord = 0
                    x_magnitude = -x_magnitude
                    
                self.rows[new_y_coord][new_x_coord] = (x_magnitude, y_magnitude)
                
        objects["->User->Command_Line"].clear()
        def decide_symbol(number):
            if number[0] or number[1]:
                return str(number[0]) + str(number[1])
            else:
                return '*'
        print '\n'.join((''.join(decide_symbol(number) for number in row) for row in self.rows))