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
    
import mpre
import mpre.base as base
import mpre.vmlibrary as vmlibrary
import mpre.authentication as authentication
import mpre.utilities as utilities
import mpre.fileio as fileio
objects = mpre.objects
Instruction = mpre.Instruction            
    
if "__file__" not in globals():
    FILEPATH = os.getcwd()
else:
    FILEPATH = os.path.split(__file__)[0]
    
class Shell(authentication.Authenticated_Client):
    """ Handles keystrokes and sends python source to the Interpreter to be executed.
        This requires authentication."""
    defaults = authentication.Authenticated_Client.defaults.copy()
    defaults.update({"username" : "root",
                     "password" : "password",
                     "prompt" : ">>> ",
                     "startup_definitions" : '',
                     "target_service" : "Interpreter"})
    
    parser_ignore = authentication.Authenticated_Client.parser_ignore + ("prompt", )
    
    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)
        self.lines = ''
        self.user_is_entering_definition = False     
        objects["Keyword_Handler"].add_keyword('', self.handle_keystrokes)
        
    def on_login(self, message):
        self.alert("{}", [message], level=0)
        sys.stdout.write(">>> ")
        self.logged_in = True
        if self.startup_definitions:
            self.handle_startup_definitions()                
             
    def handle_startup_definitions(self):
        try:
            compile(self.startup_definitions, "Shell", 'exec')
        except:
            self.alert("Startup defintions failed to compile:\n{}",
                    [traceback.format_exc()],
                    level=0)
        else:
            self.execute_source(self.startup_definitions) 
                    
    def handle_keystrokes(self, keyboard_input):
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
        if not self.logged_in:
            self.login()
        else:
            Instruction(self.target_service, "exec_code",
                        source).execute(host_info=self.host_info,
                                        callback=self.result)
                        
    def result(self, packet):
        if not packet:
            return
        if isinstance(packet, BaseException):
            raise packet
        else:
            sys.stdout.write(packet)# + self.prompt)
        
        
class Interpreter(authentication.Authenticated_Service):
    """ Executes python source. Requires authentication. The source code and 
        return value of all requests are logged.
        
        usage: Instruction("Interpreter", "exec_code",
                           my_source).execute(host_info=target_host)"""
    
    defaults = authentication.Authenticated_Service.defaults.copy()
    defaults.update({"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.'})
    
    def __init__(self, **kwargs):
        self.user_namespaces = {}
        self.user_session = {}
        super(Interpreter, self).__init__(**kwargs)
        self.log = self.create("fileio.File", "{}.log".format(self.instance_name), 'a+', persistent=False)
                
    def login(self, username, credentials):
        response = super(Interpreter, self).login(username, credentials)
        if username in self.user_secret:
            sender = self.requester_address
            self.user_namespaces[username] = {"__name__" : "__main__",
                                              "__doc__" : '',
                                              "Instruction" : Instruction}
            self.user_session[username] = ''
            string_info = (username, sender, sys.version, sys.platform, self.copyright)        
            response = ("Welcome {} from {}\nPython {} on {}\n{}\n".format(*string_info), response[1])
        return response
    
    @authentication.blacklisted
    @authentication.whitelisted
    @authentication.authenticated
    def exec_code(self, source):
        log = self.log        
        sender = self.requester_address
        username = self.logged_in[sender]
        log.write("{} {} from {}:\n".format(time.asctime(), username, sender) + 
                  source)                  
        result = ''                
        try:
            code = compile(source, "<stdin>", 'exec')
        except (SyntaxError, OverflowError, ValueError):
            result = traceback.format_exc()           
        else:                
            backup = sys.stdout            
            sys.stdout = StringIO.StringIO()
            
            namespace = (globals() if username == "root" else 
                         self.user_namespaces[username])
            remove_builtins = False
            if "__builtins__" not in namespace:
                remove_builtins = True
                namespace["__builtins__"] = __builtins__
            try:
                exec code in namespace
            except BaseException as error:
                if type(error) == SystemExit:
                    raise
                else:
                    result = traceback.format_exc()
            else:
                self.user_session[username] += source
            finally:
                if remove_builtins:
                    del namespace["__builtins__"]
                sys.stdout.seek(0)
                result = sys.stdout.read() + result
                log.write("{}\n".format(result))
                
                sys.stdout.close()
                sys.stdout = backup                
        log.flush()        
        return result
        
    def __setstate__(self, state):     
        super(Interpreter, self).__setstate__(state)
        sender = dict((value, key) for key, value in self.logged_in.items())
        for username in self.user_session.keys():
            source = self.user_session[username]
            self.user_session[username] = ''
            result = self.exec_code(sender[username], source)
                   
            
class Metapython(base.Base):
    """ The "main" class. Provides an entry point to the environment. 
        Instantiating this component and calling the start_machine method 
        starts the execution of the Processor component.
        
        startup"""

    defaults = base.Base.defaults.copy()
    defaults.update({"command" : os.path.join(FILEPATH, "shell_launcher.py"),
                     "environment_setup" : ["PYSDL2_DLL_PATH = C:\\Python27\\DLLs"],
                     "startup_components" : (#"mpre.fileio.File_System",
                                             "mpre.vmlibrary.Processor",
                                             "mpre.userinput.User_Input",
                                             "mpre.userinput.Keyword_Handler",
                                             "mpre.network.Network", "mpre.rpc.RPC_Handler",
                                             "mpre.srp.Secure_Remote_Password"),
                     "prompt" : ">>> ",
                     "copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
                     "interpreter_enabled" : True,
                     "startup_definitions" : ''})    
    parser_ignore = base.Base.parser_ignore + ("environment_setup", "prompt", "copyright", 
                                               "traceback", "interpreter_enabled",
                                               "startup_components", "startup_definitions")
                     
    # make an optional "command" positional argument and allow both -h and --help flags
    parser_modifiers = {"command" : {"types" : ("positional", ),
                                     "nargs" : '?'},
                        "help" : {"types" : ("short", "long"),
                                  "nargs" : '?'}
                        }
    exit_on_help = False

    def __init__(self, **kwargs):
        super(Metapython, self).__init__(**kwargs)
        self.setup_os_environ()
        for component_type in self.startup_components:
            component = self.create(component_type)
            setattr(self, component.instance_name.lower(), component)
            
        if self.startup_definitions:
            self.exec_command(self.startup_definitions)           
                        
        if self.interpreter_enabled:
            self.interpreter = self.enable_interpreter()
                 
        with open(self.command, 'r') as module_file:
            source = module_file.read()
            
        Instruction(self.instance_name, "exec_command", source).execute()
             
    def exec_command(self, source):
        """ Executes the supplied source as the __main__ module"""
        code = compile(source, 'Metapython', 'exec')
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
        """ This method is called automatically in Metapython.__init__; os.environ can
            be customized on startup via modifying Metapython.defaults["environment_setup"].
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
        self.processor.run()
    
    def enable_interpreter(self):      
        return self.create(Interpreter)      
        
    def exit(self, exit_code=0):
        objects["Processor"].set_attributes(running=False)
        # cleanup/finalizers go here?
        raise SystemExit
        #sys.exit(exit_code)