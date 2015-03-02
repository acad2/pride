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

import base
import vmlibrary
import network2
import utilities
import defaults
Instruction = base.Instruction            
            
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
                try:
                    compile(self.startup_definitions, "Shell", 'exec')
                except:
                    self.alert("Startup defintions failed to compile:\n{}",
                            [traceback.format_exc()],
                            level=0)
                else:
                    self.execute_source(self.startup_definitions) 

        return response
        
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
            """self.user_namespaces[username] = {"__builtins__": __builtins__,
                                              "__name__" : "__main__",
                                              "__doc__" : '',
                                              "Instruction" : Instruction}"""
                       
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
                exec code in globals()#self.user_namespaces[username]
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
        self.processor = self.create("vmlibrary.Processor")
        self.setup_os_environ()
        
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
            user_module.close()

        if self.startup_definitions:
            Instruction(self.instance_name, "exec_command", 
                        self.startup_definitions).execute()            
        Instruction(self.instance_name, "exec_command", source).execute()
                    
        self.processor.run()       
    
    def start_service(self):
        server_options = {"name" : self.instance_name,
                          "interface" : self.interface,
                          "port" : self.port}  

        self.server = self.create(Interpreter_Service, **server_options)      
        
    def exit(self, exit_code=0):
        Instruction("Processor", "attribute_setter", running=False).execute()
        # cleanup/finalizers go here?

    def save_state(self):        
        with open(self._suspended_file_name, 'wb') as pickle_file:
            pickle.dump(self.environment, pickle_file)
            pickle.dump(self, pickle_file)
            pickle_file.flush()
            pickle_file.close()
            
    @staticmethod
    def load_state(pickle_filename):
        with open(pickle_filename, 'rb') as pickle_file:
            environment = pickle.load(pickle_file)
            interpreter = pickle.load(pickle_file)
            pickle_file.close()
        interpreter.environment.update(environment)
        interpreter.processor = interpreter.create("vmlibrary.Processor")
        interpreter.setup_os_environ()            
        return interpreter
        
    
if __name__ == "__main__":
    metapython = Metapython(parse_args=True)
    metapython.start_machine()
    metapython.alert("{} shutting down", [metapython.instance_name], level='v')