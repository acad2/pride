#!/usr/bin/env python
from __future__ import unicode_literals

import sys
import codeop
import os
import traceback
import time
import cStringIO as StringIO
import importlib
import copy
import pickle

import mpre
import mpre.base as base
import mpre.vmlibrary as vmlibrary
import mpre.network2 as network2
import mpre.utilities as utilities
import mpre.fileio as fileio
import mpre.defaults as defaults

Instruction = mpre.Instruction            
            
class Shell(network2.Authenticated_Client):
    
    defaults = defaults.Shell
                     
    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)
        self.lines = ''
        self.user_is_entering_definition = False            
        self.reaction("User_Input", "add_listener " + self.instance_name)
        
    def login_result(self, sender, packet):
        response = super(Shell, self).login_result(sender, packet)
        if self.logged_in:
            sys.stdout.write(">>> ")
            if self.startup_definitions:
                self.handle_startup_definitions()                
        return response
     
    def handle_startup_definitions(self):
        try:
            compile(self.startup_definitions, "Shell", 'exec')
        except:
            self.alert("Startup defintions failed to compile:\n{}",
                    [traceback.format_exc()],
                    level=0)
        else:
            self.execute_source(self.startup_definitions) 
                    
    def handle_keystrokes(self, sender, keyboard_input):
        if not self.logged_in:
            return
        
        self.lines += keyboard_input
        lines = self.lines
                
        if lines != "\n":            
            try:
                code = codeop.compile_command(lines, "<stdin>", "exec")
            except (SyntaxError, OverflowError, ValueError) as error:
                sys.stdout.write(traceback.format_exc())
                self.prompt = ">>> "
                self.lines = ''
            else:
                if code:
                    if self.user_is_entering_definition:
                        if lines[-2:] == "\n\n":
                            self.prompt = ">>> "
                            self.lines = ''
                            self.execute_source(lines)
                            self.user_is_entering_definition = False              
                    else:
                        self.lines = ''
                        self.execute_source(lines)
                else:
                    self.user_is_entering_definition = True
                    self.prompt = "... "
        else:
            self.lines = ''
        
        sys.stdout.write(self.prompt)
        
    def execute_source(self, source):
        self.reaction(self.target, self.exec_code_request(self.target, source))
        
    def exec_code_request(self, sender, source):
        if not self.logged_in:
            response = self.login(sender, source)
        else:
            self.respond_with(self.result)
            response = "exec_code " + source
        return response     
        
    def result(self, sender, packet):
        if packet:
            sys.stdout.write("\b"*4 + "   " + "\b"*4 + packet)

    def __setstate__(self, state):
        super(Shell, self).__setstate__(state)
        Instruction(self.instance_name, "handle_startup_definitions").execute()
        
        
class Interpreter_Service(network2.Authenticated_Service):
    
    defaults = defaults.Interpreter_Service
    
    def __init__(self, **kwargs):
        self.user_namespaces = {}
        super(Interpreter_Service, self).__init__(**kwargs)
        self.log_file = open("Metapython.log", 'a')
        
    def login(self, sender, packet):
        response = super(Interpreter_Service, self).login(sender, packet)
        if "success" in response.lower():
            username = self.logged_in[sender]
            #self.user_namespaces[username] = {"__builtins__": __builtins__,
             #                                 "__name__" : "__main__",
              #                                "__doc__" : '',
               #                               "Instruction" : Instruction}
                       
            string_info = (username, sender,
                           sys.version, sys.platform, self.copyright)
        
            greeting = ("Welcome {} from {}\nPython {} on {}\n{}\n".\
                        format(*string_info))
            response = "login_result success " + greeting

        return response
        
    @network2.Authenticated
    def exec_code(self, sender, packet):
        log = self.log_file
        
        username = self.logged_in[sender]
        log.write("{} {} from {}:\n".format(time.asctime(), username, sender) + 
                  packet)
        result = ''        
        try:
            code = compile(packet, "<stdin>", 'exec')
        except (SyntaxError, OverflowError, ValueError):
            result = traceback.format_exc()
           
        else:                
            backup = sys.stdout            
            sys.stdout = StringIO.StringIO()
            
            try:
                exec code in globals() #self.user_namespaces[username]
            except BaseException as error:
                if type(error) == SystemExit:
                    raise
                else:
                    result = traceback.format_exc()
            finally:
                sys.stdout.seek(0)
                result += sys.stdout.read()
                
                sys.stdout.close()
                sys.stdout = backup
                
                log.write("{}\n".format(result))
        log.flush()
        
        return "result " + result
    
    
class Alert_Handler(base.Reactor):
    
    level_map = {0 : "",
                'v' : "notification ",
                'vv' : "verbose notification ",
                'vvv' : "very verbose notification ",
                'vvvv' : "extremely verbose notification "}
                
    defaults = defaults.Alert_Handler
             
    def __init__(self, **kwargs):
        kwargs["parse_args"] = True
        super(Alert_Handler, self).__init__(**kwargs)
        self.log = fileio.File(self.log_name, 'a')
        
    def alert(self, message, level, callback):      
        if not self.print_level or level <= self.print_level:
            sys.stdout.write(message + "\n")
        if level <= self.log_level:
            severity = self.level_map.get(level, str(level))
            self.log.write(severity + message + "\n")

        if callback:
            function, args, kwargs = callback
            return function(*args, **kwargs)

            
class Metapython(base.Reactor):

    defaults = defaults.Metapython
        
    parser_ignore = ("environment_setup", "prompt", "copyright", 
                     "traceback", "memory_size", "network_packet_size", 
                     "interface", "port")
                     
    parser_modifiers = {"command" : {"types" : ("positional", ),
                                     "nargs" : '?'},
                        "help" : {"types" : ("short", "long"),
                                  "nargs" : '?'}
                        }
    exit_on_help = False

    def __init__(self, **kwargs):
        super(Metapython, self).__init__(**kwargs)
        self.setup_os_environ()
        self.processor = self.create("vmlibrary.Processor")        
        self.alert_handler = self.create(Alert_Handler)

        if self.startup_definitions:
            Instruction(self.instance_name, "exec_command", 
                        self.startup_definitions).execute() 
                        
        if self.interpreter_enabled:
            Instruction(self.instance_name, "start_service").execute()
                       
    def exec_command(self, source):
        code = compile(source, 'Metapython', 'exec')
        
        exec code in globals(), globals()

    def setup_os_environ(self):
        modes = {"=" : "equals",
                 "+=" : "__add__", # append strings or add ints
                 "-=" : "__sub__", # integer values only
                 "*=" : "__mul__",
                 "/=" : "__div__"}

        for command in self.environment_setup:
            variable, mode, value = command.split()
            if modes[mode] == "equals":
                result = value
            else:
                environment_value = os.environ[variable]
                method = modes[mode]
                result = getattr(environment_value, method)(value)
            os.environ[variable] = result
            
    def start_machine(self):
        with open(self.command, 'r') as user_module:
            source = user_module.read()
                       
        Instruction(self.instance_name, "exec_command", source).execute()
                   
        self.processor.run()       
    
    def start_service(self):
        server_options = {"name" : self.instance_name,
                          "interface" : self.interface,
                          "port" : self.port}  
        
        self.server = self.create(Interpreter_Service, **server_options)      
        
    def exit(self, exit_code=0):
        Instruction("Processor", "set_attributes", running=False).execute()
        # cleanup/finalizers go here?

    def save_state(self):
        """ usage: metapython.save_state()
        
            Stores a snapshot of the current runtime environment. 
            This file is saved as metapython._suspended_file_name, which
            defaults to "suspended_interpreter.bin"."""            
        with open(self._suspended_file_name, 'wb') as pickle_file:
            pickle.dump(self.environment, pickle_file)            
            pickle_file.flush()
            pickle_file.close()
                    
    @staticmethod
    def load_state(pickle_filename):
        """ usage: from metapython import *
                    Metapython.load_state(pickle_filename) => interpreter
                    
            Load an environment that was saved by Metapython.save_state.
            The package global mpre.environment is updated with the
            contents of the restored environment, and the component at
            environment.Component_Resolve["Metapython"] is returned by this
            method.
            
            """
        import mpre
        
        with open(pickle_filename, 'rb') as pickle_file:
            mpre.environment.update(pickle.load(pickle_file))
            pickle_file.close()

        interpreter = mpre.environment.Component_Resolve["Metapython"]
        interpreter.setup_os_environ()
        return interpreter
        
 
class Restored_Interpreter(Metapython):
    """ usage: Restored_Intepreter(filename="suspended_interpreter.bin") => interpreter
    
        Restores an interpreter environment that has been suspended via
        metapython.Metapython.save_state. This is a convenience class
        over Metapython.load_state; instances produced by instantiating
        Restored_Interpreter will be of the type of instance returned by
        Metapython.load_state and not Restored_Interpreter"""
        
    defaults = defaults.Metapython.copy()
    defaults.update({"filename" : 'suspended_interpreter.bin'})
    
    def __new__(cls, *args, **kwargs):
        instance = super(Restored_Interpreter, cls).__new__(cls, *args, **kwargs)
        attributes = cls.defaults.copy()
        if kwargs.get("parse_args"):
            attributes.update(instance.parser.get_options(cls.defaults))       
        
        return Metapython.load_state(attributes["filename"])
        
if __name__ == "__main__":
    metapython = Metapython(verbosity='vvv', parse_args=True)
    metapython.start_machine()
    metapython.alert("{} shutting down", [metapython.instance_name], level='v')