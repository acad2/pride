#   mpf.interpreter - python interpreter with remote access
#
#    Copyright (C) 2014  Ella Rose
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import codeop # compile_command

import base
import defaults
Event = base.Event

class Shell(base.Process):
    """Interactive Interpreter that can be used simultaneously with running
    python scripts."""
    
    defaults = defaults.Shell
    hotkeys = {}
    
    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)
        self.line = []
        self.lines = []
        options = {"target" : (self.host_name, self.port),
        "incoming" : self._incoming,
        "outgoing" : self._outgoing,
        "on_connection" : self._on_connection}        
        
        self.connection = self.create("networklibrary.Outbound_Connection", **options)  
        self.keyboard = self.create("vmlibrary.Keyboard")
        
    def run(self):        
        if self.network_buffer:
            sys.stdout.write(self.network_buffer+self.prompt)
            self.network_buffer = None
            
        if self.keyboard.input_waiting():
            self.keyboard.get_line(self)     
            
        if self.keyboard_input:
            for character in self.keyboard_input:
                if character == u'\n':
                    self._handle_return() 
                else:
                    self.line.append(character)
            self.keyboard_input = ''
        
        self.propagate()
            
    def _handle_return(self):
        line = ''.join(self.line)
        
        if line == "": # finished entering defintion
            self.definition = False
        self.lines.append(line+"\n")
        lines = "".join(self.lines)
        try:
            code = codeop.compile_command(lines, "<stdin>", "exec")
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
                Event("Asynchronous_Network0", "buffer_data", self.connection, lines).post()
            else:
                self.definition = True
                self.prompt = "... "
        sys.stdout.write(self.prompt)
        self.line = [] 
        
    def _outgoing(self, sock, data):
        sock.send(data)
        
    def _incoming(self, sock):
        self.network_buffer = sock.recv(self.network_chunk_size)
                              
    def _on_connection(self, connection, address):
        self.connection = connection
        self.login_thread = self.create("networklibrary.Basic_Authentication_Client")    
        Event(self.instance_name, "_login", component=self).post()
        
    def _login(self):
        try:
            self.login_thread.run()
        except StopIteration:
            self.login_thread.delete()
            del self.login_thread
            Event(self.instance_name, "run").post()
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
                    Event("Asynchronous_Network0", "buffer_data", self.connection, self.startup_definitions+"\n").post()
                    sys.stdout.write("Attempting to compile startup definitions...\n%s" % self.prompt)
        else:
            Event(self.instance_name, "_login", component=self).post()
        
        
class Shell_Service(base.Process):
    """Interactive Interpreter that can be used simultaneously with running
    python scripts. Also allows for remote access"""
    
    defaults = defaults.Shell_Service
        
    def __init__(self, **kwargs):
        super(Shell_Service, self).__init__(**kwargs)
        self.line = []
        self.lines = []
        self.login_stage = {}
        self.network_buffer = {}
        self.login_threads = []
        self.authenticate = {"root" : hash("password")}
        self.client_namespaces = {}
        self.swap_file = open("sssf", "w+")
        self.log_file = open("%s log" % self.__class__.__name__, "w")
        
        options = {"incoming" : self._read_socket,
                   "outgoing" : self._write_socket,
                   "on_connection" : self._on_connection,
                   "name" : "Remote_Console_Service",
                   "interface" : self.interface,
                   "port" : self.port}
        Event("Asynchronous_Network0", "create", "networklibrary.Server", **options).post()
                
    def _on_connection(self, connection, address):
        self.network_buffer[connection] = None
        login_thread = self.create("networklibrary.Basic_Authentication", connection, address)
        self.login_threads.append(login_thread)
        self.login_stage[address] = "Beginning..."
        
    def _read_socket(self, connection):
        self.network_buffer[connection] = connection.recv(8096)
              
    def _write_socket(self, connection, data):
        connection.send(data)
        
    def run(self):
        for login_thread in self.login_threads:
            try:
                login_thread.run()
            except StopIteration:       
                connection = login_thread.connection
                address = login_thread.address
                username, status  = self.login_stage[address]
                response = "Welcome %s from (%s)" % (username, address)\
                +"\nPython %s on %s\n%s\n(%s)\n" % \
                (sys.version, sys.platform, self.copyright, self.__class__.__name__)
                Event("Asynchronous_Network0", "buffer_data", connection, response).post()
                self.login_stage[address] = (username, "online/active")
                
                self.network_buffer[connection] = ""
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
            Event(self.instance_name, "run", component=self).post()
            
    def _main(self, connection, input):     
        sys.stdout = self.swap_file
        code = self._compile(input)
        if code:
            self.execute_code(code)
            
        sys.stdout.seek(0)
        results = sys.stdout.read()
        if results:
            self.log_file.write("Results: " + results)
            Event("Asynchronous_Network0", "buffer_data", connection, results).post()
        sys.stdout.seek(0)
        sys.stdout.truncate() # delete contents
        sys.stdout = sys.__stdout__
            
    def _compile(self, input):
        try:
            code = codeop.compile_command(input, "<stdin>", "exec")
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
            sys.stdout = self.swap_file # can be changed by code and not changed back
            if type(error) == SystemExit:
                raise
            else:
                sys.stdout.write(self.traceback())
            
    def __del__(self):
        for connection in self.network_buffer.keys():
            print "informing %s that %s is shutting down" % (connection.getpeername(), self)
            Event("Asynchronous_Network0", "buffer_data", connection, "Service shutting down").post()
