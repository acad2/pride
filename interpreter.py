import sys
from codeop import CommandCompiler

import base
import defaults
from eventlibrary import Event


class Shell(base.Process):
    """Interactive Interpreter that can be used simultaneously with running
    python scripts."""
    
    defaults = defaults.Shell
    compile = CommandCompiler()
    hotkeys = {}
    
    def __init__(self, *args, **kwargs):
        super(Shell, self).__init__(*args, **kwargs)
        self.line = []
        self.lines = []
        options = {"target" : (self.host_name, self.port),
        "incoming" : self.incoming,
        "outgoing" : self.outgoing,
        "on_connection" : self.on_connection}        
        
        self.connection = self.create("networklibrary.Outbound_Connection", **options)  
    
    def run(self):    
        
        if self.network_buffer:
            sys.stdout.write(self.network_buffer+self.prompt)
            self.network_buffer = None
            
        if self.parent.objects["Keyboard"][0].input_waiting(): # msvcrt.kbhit
            character = self.parent.objects["Keyboard"][0].get_input() # msvcrt.getwch
            if character == "\t": # don't even try to deal with tabs
                character = "    "            

            if character == u'\r':
                self.handle_return() 
            elif character == u'\b':
                sys.stdout.write(character)
                self.handle_backspace()
            else:
                sys.stdout.write(character) 
                self.line.append(character)
            
        Event("Shell", "run").post()
        
    def handle_backspace(self):
        line = ''.join(self.line)
        if line != u"\n":
            try:
                char = self.line.pop()
                if char == "    ":
                    sys.stdout.write(" \b\b\b\b")
                else:
                    sys.stdout.write(" \b")
            except IndexError:
                sys.stdout.write(" ")
        else:
            sys.stdout.write(" ")
            
    def handle_return(self):
        line = ''.join(self.line)
        
        if line == "": # finished entering defintion
            self.definition = False
        self.lines.append(line+"\n")
        lines = "".join(self.lines)
        sys.stdout.write("\n")
        try:
            code = self.compile(lines, "<stdin>", "exec")
        except (SyntaxError, OverflowError, ValueError) as error: # did not compile
            if type(error) == SyntaxError:
                sys.stdout.write(self.traceback())
                self.prompt = ">>> "
                self.lines = []
            else:
                self.prompt = "... "
        else:
            if code and not self.definition:
                self.prompt = ">>> "
                self.lines = []
                Event("Network_Manager", "buffer_data", self.connection, lines).post()
            else:
                self.definition = True
                self.prompt = "... "
        sys.stdout.write(self.prompt)
        self.line = [] 
        
    def outgoing(self, sock, data):
        sock.send(data)
        
    def incoming(self, sock):
        self.network_buffer = sock.recv(2048)
                              
    def on_connection(self, connection, address):
        self.connection = connection
        self.login_thread = self.create("networklibrary.Basic_Authentication_Client")    
        Event("Shell", "login").post()
        
    def login(self):
        try:
            self.login_thread.run()
        except StopIteration:
            self.login_thread.delete()
            Event("Shell", "run").post()
            print self.network_buffer
            self.network_buffer = None
            sys.stdout.write(self.prompt)
            self.login_stage = None            
            if self.startup_definitions:
                try:
                    compile(self.startup_definitions, "startup_definition", "exec")
                except:
                    print "startup definitions failed to compile"                    
                else:
                    Event("Network_Manager", "buffer_data", self.connection, self.startup_definitions+"\n").post()
                    sys.stdout.write("Attempting to compile startup definitions...\n%s" % self.prompt)
        else:
            Event("Shell", "login").post()
        
        
class Shell_Service(base.Process):
    """Interactive Interpreter that can be used simultaneously with running
    python scripts. features non blocking input and threadless concurrency."""
    
    defaults = defaults.Shell_Service
    compile = CommandCompiler()
    
    def __init__(self, *args, **kwargs):
        super(Shell_Service, self).__init__(*args, **kwargs)
        self.line = []
        self.lines = []
        self.login_stage = {}
        self.network_buffer = {}
        self.login_threads = []
        self.authenticate = {"root" : hash("password")}
        self.client_namespaces = {}
        self.swap_file = open("sssf", "w+")
        self.log_file = open("%s log" % self.__class__.__name__, "w")
        
        Event("Network_Manager", "create", "networklibrary.Server", \
        incoming=self.read_socket, outgoing=self.write_socket, on_connection=self.on_connection, \
        name="Remote_Console_Service", host_name=self.host_name, port=self.port).post()
                
    def on_connection(self, connection, address):
        self.network_buffer[connection] = None
        login_thread = self.create("networklibrary.Basic_Authentication", connection, address)
        self.login_threads.append(login_thread)
        self.login_stage[address] = "Beginning..."
        
    def read_socket(self, connection):
        self.network_buffer[connection] = connection.recv(8096)
              
    def write_socket(self, connection, data):
        connection.send(data)
        
    def run(self):
        for login_thread in self.login_threads:
            try:
                login_thread.run()
            except StopIteration:           
                address = login_thread.address
                username, status  = self.login_stage[address]
                response = "Welcome %s from (%s)" % (username, address)\
                +"\nPython %s on %s\n%s\n(%s)\n" % \
                (sys.version, sys.platform, self.copyright, self.__class__.__name__)
                Event("Network_Manager", "buffer_data", login_thread.connection, response).post()
                self.login_stage[address] = (username, "online/active")
                self.network_buffer[login_thread.connection] = ""
                self.login_threads.remove(login_thread)
                login_thread.delete()        
                
                # controls namespace that clients have access to        
                #self.client_namespaces[connection] = {"__builtins__" : globals()["__builtins__"], \
                #"__doc__" : globals()["__doc__"], \
                #"__name__" : "%s __main__" % username, \
                #"Event" : Event, \
                #self.parent.name : self.parent}
        
        for client in self.network_buffer.keys():
            if type(self.login_stage[client.getpeername()]) == tuple:
                input = self.network_buffer[client]
                self.network_buffer[client] = None
                if input:
                    self._main(client, input)
         
        if self in self.parent.objects["Shell_Service"]:
            Event("Shell_Service", "run").post()
            
    def _main(self, connection, input):     
        sys.stdout = self.swap_file
        code = self.compile(input)
        if code:
            self.execute_code(code)
            
        sys.stdout.seek(0)
        results = sys.stdout.read()
        if results:
            self.log_file.write("Results: " + results)
            Event("Network_Manager", "buffer_data", connection, results).post()
        sys.stdout.seek(0)
        sys.stdout.truncate() # delete contents
        sys.stdout = sys.__stdout__
            
    def compile(self, input):
        try:
            code = compile(input, "<stdin>", "exec")
        except (SyntaxError, OverflowError, ValueError) as error: # did not compile
            if type(error) == SyntaxError:
                sys.stdout.write(self.traceback())
        else:
            self.log_file.write("Command:\n"+input)
            return code                                                                                         
        
    def execute_code(self, code):
        try:
            exec code in locals(), globals()
        except BaseException as error:
            if type(error) == SystemExit:
                raise
            else:
                sys.stdout.write(self.traceback())
            
    def __del__(self):
        for connection in self.network_buffer.keys():
            print "informing %s that %s is shutting down" % (connection.getpeername(), self)
            Event("Network_Manager", "buffer_data", connection, "Service shutting down").post()
