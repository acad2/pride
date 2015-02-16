#!/usr/bin/env python
from __future__ import unicode_literals

import sys
import codeop
import os
import tempfile
import traceback
import time
import cStringIO as StringIO
from contextlib import closing

import base
import vmlibrary
import network2
import utilities
import defaults
Instruction = base.Instruction


class Interpreter_Client(network2.Authenticated_Client):
    
    defaults = defaults.Authenticated_Client.copy()
    defaults.update({"username" : "ellaphant",
                     "password" : "puppydog",
                     "email" : "notneeded@no.com",
                     "startup_definitions" : '',
                     "target" : ("localhost", 40022)})
                     
    def __init__(self, **kwargs):
        super(Interpreter_Client, self).__init__(**kwargs)
                
    def login_result(self, sender, packet):
        response = super(Interpreter_Client, self).login_result(sender, packet)
        if self.logged_in:
            sys.stdout.write(">>> ")
            if self.startup_definitions:
                try:
                    compile(self.startup_definitions, "Interpreter_Client", 'exec')
                except:
                    self.alert("Startup defintions failed to compile:\n{}",
                            [traceback.format_exc()],
                            level=0)
                else:
                    self.execute_source(self.startup_definitions) 

        return response
        
    def execute_source(self, source):
        self.rpc(self.target, self.exec_code_request(self.target, source))
        
    def exec_code_request(self, sender, source):
        if not self.logged_in:
            response = self.login(sender, source)
        else:
            response = "return result exec_code " + source
        return response     
        
    def result(self, sender, packet):
        if packet:
            sys.stdout.write("\b"*4 + "   " + "\b"*4 + packet + ">>> ")
        
        
class Interpreter_Service(network2.Authenticated_Service):
    
    defaults = defaults.Authenticated_Service
    defaults.update({"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
                     "port" : 40022,
                     "interface" : "0.0.0.0"})
    
    def __init__(self, **kwargs):
        self.user_namespaces = {}
        super(Interpreter_Service, self).__init__(**kwargs)
        self.log_file = open("Metapython.log", 'a')
        
    def login(self, sender, packet):
        response = super(Interpreter_Service, self).login(sender, packet)
        if "success" in response.lower():
            username = self.logged_in[sender]
            self.user_namespaces[username] = {"__builtins__": __builtins__,
                                              "__name__" : "__main__",
                                              "__doc__" : '',
                                              "Instruction" : Instruction}
                       
            string_info = (username, sender,
                           sys.version, sys.platform, self.copyright)
        
            greeting = ("Welcome {} from {}\nPython {} on {}\n{}\n".\
                        format(*string_info))
            response = "end_request login_result success " + greeting

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
                exec code in self.user_namespaces[username]
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
        return result

        
class Shell(base.Base):
    """Captures user input and passes it to Interpreter_Client"""

    defaults = defaults.Shell
    
    exit_on_help = True
    parser_ignore = ("copyright", "traceback")
    
    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)
        self.lines = ''
        self.user_is_entering_definition = False
        self.interpreter = self.create(Interpreter_Client)
            
        self.rpc("User_Input", "add_listener " + self.instance_name)
        self.definition_finished = False
                
    def handle_keystrokes(self, sender, keyboard_input):
     #   sys.stdout.write(self.instance_name + " received keystrokes " + keyboard_input)
        self.lines += keyboard_input
        lines = self.lines
                
        if lines != "\n":            
            try:
                code = codeop.compile_command(lines, "<stdin>", "exec")
            except (SyntaxError, OverflowError, ValueError) as error:
                sys.stdout.write(traceback.format_exc())
                raise SystemExit
                self.prompt = ">>> "
                self.lines = ''
            else:
                if code:
                    if self.user_is_entering_definition:
                        if lines[-2:] == "\n\n":
                            self.prompt = ">>> "
                            self.lines = ''
                            self.interpreter.execute_source(lines)
                            self.user_is_entering_definition = False
                        
                    else:
                        self.lines = ''
                        self.interpreter.execute_source(lines)
                else:
                    self.user_is_entering_definition = True
                    self.prompt = "... "
        else:
            self.lines = ''
        
        sys.stdout.write(self.prompt)
            
    
class Metapython(base.Base):

    defaults = defaults.Metapython

    parser_ignore = ("environment_setup", "prompt", "copyright", "authentication_scheme",
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
                
        self.setup_environment()
        
        if self.interpreter_enabled:
            Instruction(self.instance_name, "start_service").execute()
       
        Instruction(self.instance_name, "exec_command").execute()
        self.start_machine()
        
        self.alert("{} shutting down", [self.instance_name], level='v')
        
    def setup_environment(self):
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
        
    def exec_command(self):
        module = open(self.command, 'r')
        code = compile(module.read(), 'Metapython', 'exec')
        
        exec code in globals(), globals()

    def start_machine(self):
        machine = self.create("vmlibrary.Machine")
        machine.create("network.Asynchronous_Network")
        machine.run()       
    
    def start_service(self):
        server_options = {"name" : self.instance_name,
                          "interface" : self.interface,
                          "port" : self.port}  
               
        self.server = self.create(Interpreter_Service, **server_options)      
        
    def exit(self, exit_code=0):
        Instruction("Processor", "attribute_setter", running=False).execute()
        # cleanup/finalizers go here?


if __name__ == "__main__":
    Metapython = Metapython(parse_args=True)