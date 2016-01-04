#!/usr/bin/env python
""" Provides classes for the launcher class and parts for an interpreter."""
import sys
import codeop
import os
import traceback
import time
import contextlib
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import pride
import pride.base as base
import pride.authentication2 as authentication2
import pride.shell

@contextlib.contextmanager
def main_as_name():
    backup = globals()["__name__"]        
    globals()["__name__"] = "__main__"
    try:
        yield
    finally:
        globals()["__name__"] = backup        
    
class Shell(authentication2.Authenticated_Client):
    """ Handles keystrokes and sends python source to the Interpreter to 
        be executed. This requires authentication via username/password."""
    defaults = {"username" : "", "password" : "", "startup_definitions" : '', 
                "target_service" : "->Python->Interpreter"}   
    
    verbosity = {"login" : 0, "execute_source" : "vv"}
                
    def on_login(self, message):
        super(Shell, self).on_login(message)        
        sys.stdout.write(">>> ")        
        if self.startup_definitions:
            self.handle_startup_definitions()                
             
    def handle_startup_definitions(self):
        source = pride.compiler.preprocess(self.startup_definitions)
        try:
            compile(source, "Shell", 'exec')
        except:
            self.alert("Startup defintions failed to compile:\n{}",
                       [traceback.format_exc()],
                       level=0)
        else:
            self.startup_definitions = ''
            self.execute_source(source)
                        
    @pride.authentication2.remote_procedure_call(callback_name="result")
    def execute_source(self, source): 
        """ Sends source to the interpreter specified in self.target_service for execution """
                                    
    def result(self, packet):
        if not packet:
            return
        if isinstance(packet, BaseException):
            raise packet
        else:
            print packet
            sys.stdout.write('\b' * 4 + packet + objects["->User->Command_Line"].prompt)
        

class Interpreter(authentication2.Authenticated_Service):
    """ Executes python source. Requires authentication from remote hosts. 
        The source code and return value of all requests are logged. """
    
    defaults = {"help_string" : 'Type "help", "copyright", "credits" or "license" for more information.',
                "login_message" : "Welcome {} from {}\nPython {} on {}\n{}\n",
                "_logger_type" : "StringIO.StringIO"}
    
    mutable_defaults = {"user_namespaces" : dict, "user_session" : dict}
    
    remotely_available_procedures = ("execute_source", "execute_instruction")
    
    def __init__(self, **kwargs):
        super(Interpreter, self).__init__(**kwargs)
        filename = '_'.join(word for word in self.reference.split("->") if word)
        self.log = self.create("pride.fileio.File", 
                               "{}.log".format(filename), 'a+',
                               persistent=False).reference
        self._logger = invoke(self._logger_type)
        
    def on_login(self):
        session_id, sender = self.current_session
        username = self.session_id[session_id]
        self.user_session[username] = ''
        string_info = (username, sender, sys.version, sys.platform, self.help_string)
        return self.login_message.format(*string_info)
        
    def execute_source(self, source):
        log = pride.objects[self.log]
        session_id, sender = self.current_session
                
        username = self.session_id[session_id]
        log.write("{} {} from {}:\n".format(time.asctime(), username, 
                                            sender) + source)           
        result = ''         
        try:
            code = pride.compiler.compile(source)
        except (SyntaxError, OverflowError, ValueError):
            result = traceback.format_exc()           
        else:               
            with sys.stdout.switched(self._logger):
                try:
                    exec code in globals()
                except Exception as result:
                    if type(result) == SystemExit:
                        raise
                    result.traceback = traceback.format_exc()
                else:
                    self.user_session[username] += source                
                    sys.stdout.seek(0)
                    result = sys.stdout.read() + result
                log.write("{}\n".format(result))                    
                sys.stdout.truncate(0)                                                 
        log.flush()        
        return result
        
    def _exec_command(self, source):
        """ Executes the supplied source as the __main__ module"""
        code = pride.compiler.compile(source, "__main__")
        with main_as_name():
            exec code in globals(), globals()
            
    def execute_instruction(self, instruction, priority, callback):
        """ Executes the supplied instruction with the specified priority and callback """
        instruction.execute(priority=priority, callback=callback)
        
        
class Python(base.Base):
    """ The "main" class. Provides an entry point to the environment. 
        Instantiating this component and calling the start_machine method 
        starts the execution of the Processor component."""
    defaults = {"command" : '',
                "environment_setup" : ("PYSDL2_DLL_PATH = " + 
                                       os.path.dirname(os.path.realpath(__file__)) +
                                       os.path.sep + "gui" + os.path.sep, ),
                "startup_components" : ("pride.vmlibrary.Processor",
                                        "pride.network.Network_Connection_Manager",
                                        "pride.network.Network", 
                                        "pride.interpreter.Interpreter",
                                        "pride.rpc.Rpc_Connection_Manager",
                                        "pride.rpc.Rpc_Server",
                                        "pride.rpc.Rpc_Worker"),
                "startup_definitions" : '',
                "interpreter_type" : "pride.interpreter.Interpreter"}
                     
    parser_ignore = ("environment_setup", "startup_components", 
                     "startup_definitions", "interpreter_type")
                     
    # make an optional "command" positional argument and allow 
    # both -h and --help flags
    parser_modifiers = {"command" : {"types" : ("positional", ),
                                     "nargs" : '?'},
                        "help" : {"types" : ("short", "long"),
                                  "nargs" : '?'},
                        "exit_on_help" : False}
    
    verbosity = {"shutdown" : 0, "restart" : 0, "os_environ_set" : 'v'}
    
    def __init__(self, **kwargs):
        super(Python, self).__init__(**kwargs)
        self.setup_os_environ()

        if self.startup_definitions:
            self.interpreter._exec_command(self.startup_definitions)           
        
        if not self.command:
            command = os.path.join((os.getcwd() if "__file__" 
                                    not in globals() else 
                                    os.path.split(__file__)[0]), 
                                    "shell_launcher.py")
        else:
            command = self.command        
        with open(command, 'r') as module_file:
            source = module_file.read()            
        pride.Instruction(self.interpreter, "_exec_command", source).execute()
             
    def setup_os_environ(self):
        """ This method is called automatically in Python.__init__; os.environ can
            be customized on startup via modifying Python.defaults["environment_setup"].
            This can be useful for modifying system path only for the duration of the applications run time.
            Currently this is only used to point to this files directory for SDL2 dll files. """
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
            self.alert("Setting os.environ[{}] = {}", (variable, result),
                       level=self.verbosity["os_environ_set"])
            os.environ[variable] = result
            
    def start_machine(self):
        """ Begins the processing of Instruction objects."""
        processor = pride.objects[self.processor]
        processor.running = True
        processor.run()
        
    def exit(self, exit_code=0):
        raise SystemExit(exit_code)
        