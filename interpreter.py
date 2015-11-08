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
import pride.vmlibrary as vmlibrary
import pride.authentication as authentication
import pride.utilities as utilities
import pride.fileio as fileio
import pride.shell
objects = pride.objects
Instruction = pride.Instruction            

    
class Shell(authentication.Authenticated_Client):
    """ Handles keystrokes and sends python source to the Interpreter to 
        be executed. This requires authentication via username/password."""
    defaults = {"username" : "",
                "password" : "",
                "prompt" : ">>> ",
                "startup_definitions" : '',
                "target_service" : "->Python->Interpreter"}
    
    parser_ignore = ("prompt", )
    
    verbosity = {"logging_in" : ''}
    
    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)
        self.lines = ''
        self.user_is_entering_definition = False     
                
    def on_login(self, message):
        self.alert("{}", [message], level='')
        sys.stdout.write(">>> ")
        self.logged_in = True
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
            self.execute_source(source)
                    
    def handle_input(self, user_input):                
        if not user_input:
            user_input = '\n'
        else:
            user_input = pride.compiler.preprocess(user_input)
            
        self.lines += user_input
        lines = self.lines
        write_prompt = True  
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
                        write_prompt = False
                else:
                    self.user_is_entering_definition = True
                    self.prompt = "... "
        else:
            self.lines = ''
        objects["->Python->Command_Line"].set_prompt(self.prompt)
        
    def execute_source(self, source):
        if not self.logged_in:
            self.alert("Not logged in. Unable to process {}".format(source))
            self.login()            
        else:
            self.session.execute(Instruction(self.target_service, "handle_input",
                                             source), callback=self.result)
                                    
    def result(self, packet):
        if not packet:
            return
        if isinstance(packet, BaseException):
            raise packet
        else:
            sys.stdout.write('\b' * 4 + packet + self.prompt)
        

class Interpreter(authentication.Authenticated_Service):
    """ Executes python source. Requires authentication from remote hosts. 
        The source code and return value of all requests are logged. """
    
    defaults = {"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
                "login_message" : "Welcome {} from {}\nPython {} on {}\n{}\n"}
    
    def __init__(self, **kwargs):
        self.user_namespaces = {}
        self.user_session = {}
        super(Interpreter, self).__init__(**kwargs)
        filename = '_'.join(word for word in self.instance_name.split("->") if word)
        self.log = self.create("fileio.File", 
                               "{}.log".format(filename), 'a+',
                               persistent=False).instance_name
                
    def login(self, username, credentials):
        response = super(Interpreter, self).login(username, credentials)
        session_id, sender = self.current_session
        if response[0] == self.login_message:
           # self.user_namespaces[username] = {"__name__" : "__main__",
           #                                   "__doc__" : '',
           #                                   "Instruction" : Instruction}
            self.user_session[username] = ''
            string_info = (username, sender, sys.version, sys.platform, 
                           self.copyright)    
            response = (self.login_message.format(*string_info), response[1])
        return response

    def handle_input(self, source):
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
            backup = sys.stdout            
            sys.stdout = StringIO.StringIO()
            
            namespace = globals()# if username == "root" else self.user_namespaces[username]
            remove_builtins = False
            if "__builtins__" not in namespace:
                remove_builtins = True
                namespace["__builtins__"] = __builtins__
            
            backup_raw_input = namespace["__builtins__"]["raw_input"]
            namespace["__builtins__"]["raw_input"] = pride.shell.get_user_input
            try:
                exec code in namespace
            except Exception as error:
                if type(error) == SystemExit:
                    raise
                else:
                    result = traceback.format_exc()
            else:
                self.user_session[username] += source
            finally:
                namespace["__builtins__"]["raw_input"] = backup_raw_input
                
                if remove_builtins:
                    del namespace["__builtins__"]
                sys.stdout.seek(0)
                result = sys.stdout.read() + result
                log.write("{}\n".format(result))
                
                sys.stdout.close()
                sys.stdout = backup           
        log.flush()        
        return result
        
        
class Python(base.Base):
    """ The "main" class. Provides an entry point to the environment. 
        Instantiating this component and calling the start_machine method 
        starts the execution of the Processor component."""
    defaults = {"command" : os.path.join((os.getcwd() if "__file__" 
                                          not in globals() else 
                                          os.path.split(__file__)[0]), 
                                          "shell_launcher.py"),
                "environment_setup" : ["PYSDL2_DLL_PATH = " + 
                                       os.path.dirname(os.path.realpath(__file__)) +
                                       os.path.sep + "gui" + os.path.sep],
                "startup_components" : ("pride.vmlibrary.Processor",
                                        "pride.network.Network", 
                                        "pride.shell.Command_Line",
                                        "pride.srp.Secure_Remote_Password",
                                        "pride.interpreter.Interpreter",
                                        "pride.rpc.Rpc_Server"),
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
    
    def __init__(self, **kwargs):
        super(Python, self).__init__(**kwargs)
        self.setup_os_environ()
        
        if self.startup_definitions:
            self._exec_command(self.startup_definitions)           
                        
        with open(self.command, 'r') as module_file:
            source = module_file.read()            
        Instruction(self.instance_name, "_exec_command", source).execute()
                
    def _exec_command(self, source):
        """ Executes the supplied source as the __main__ module"""
        code = pride.compiler.compile(source, "__main__")
        with self.main_as_name():
            exec code in globals(), globals()
            
    @contextlib.contextmanager
    def main_as_name(self):
        backup = globals()["__name__"]        
        globals()["__name__"] = "__main__"
        try:
            yield
        finally:
            globals()["__name__"] = backup
             
    def setup_os_environ(self):
        """ This method is called automatically in Python.__init__; os.environ can
            be customized on startup via modifying Python.defaults["environment_setup"].
            This can be useful for modifying system path only for the duration of the applications run time."""
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
        """ Begins the processing of Instruction objects."""
        processor = pride.objects[self.processor]
        processor.running = True
        processor.run()
        self.alert("Graceful shutdown initiated", level='v')
        
    def exit(self, exit_code=0):
        pride.objects[self.processor].running = False
        # cleanup/finalizers go here?
        sys.exit(exit_code)
        