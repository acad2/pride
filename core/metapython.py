#!/usr/bin/env python

import sys
import codeop
import os
import tempfile
from contextlib import closing

import base
import vmlibrary
import utilities
import defaults
Instruction = base.Instruction

stdin = vmlibrary.stdin

class Shell(vmlibrary.Process):
    """(Potentially remote) connection to the interactive interpreter"""

    defaults = defaults.Shell
    hotkeys = {}

    exit_on_help = True
    parser_ignore = ("copyright", "traceback", "copyright")

    def __init__(self, **kwargs):
        super(Shell, self).__init__(**kwargs)
        self.line = []
        self.lines = []
        options = {"target" : (self.ip, self.port),
                   "on_connect" : self._on_connect,
                   "socket_send" : self._socket_send,
                   "socket_recv" : self._socket_recv}

        self.connection = self.create("networklibrary.Outbound_Connection", **options)
        self.network_buffer[self.connection] = ''
        self.keyboard = self.create("keyboard.Keyboard")
        self.definition = False

    def run(self):
        connection = self.connection
        if self.network_buffer[connection]:
            sys.stdout.write(self.network_buffer[connection]+self.prompt)
            self.network_buffer[connection] = ''

        if self.keyboard.input_waiting():
            self.keyboard.get_line(self)

        if self.keyboard_input:
            for character in self.keyboard_input:
                if character == u'\n':
                    self._handle_return()
                else:
                    self.line.append(character)
            self.keyboard_input = ''

        self.run_instruction.execute()

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
                Instruction("Asynchronous_Network", "buffer_data", self.connection, lines).execute()
            else:
                self.definition = True
                self.prompt = "... "
        sys.stdout.write(self.prompt)
        self.line = []

    def _socket_send(self, connection, data):
        connection.send(data)

    def _socket_recv(self, connection):
        self.network_buffer[connection] = connection.recv(self.network_packet_size)

    def _on_connect(self, connection):
        self.connection = connection
        options = {"auto_login" : self.auto_login,
                   "credentials" : (self.username, self.password),
                   "handle_success" : self._on_login_success,
                   "wait" : self._on_wait,
                   "network_buffer" : self.network_buffer,
                   "connection" : connection}

        Instruction("Asynchronous_Network", "add", connection).execute()
        self.login_thread = self.create("networklibrary.Basic_Authentication_Client",
                                        **options)
        self.process("_login")

    def _on_login_success(self, connection):
        self.process("run")
        print self.network_buffer[connection]
        self.network_buffer[connection] = ''
        sys.stdout.write(self.prompt)
        if self.startup_definitions:
            try:
                compile(self.startup_definitions, "startup_definition", "exec")
            except:
                args = (self.instance_name, self.traceback())
                self.alert("{0} startup definitions failed to compile\n{1}",
                           args, 0)
            else:
                Instruction("Asynchronous_Network", "buffer_data", self.connection, self.startup_definitions+"\n").execute()

    def _on_wait(self):
        self.process("_login")

    def _login(self):
        self.login_thread.run()


class Metapython(vmlibrary.Process):

    defaults = defaults.Metapython

    parser_ignore = ("environment_setup", "prompt", "copyright", "authentication_scheme",
                     "auto_start", "keyboard_input", "traceback", "pypy", "jython",
                     "python", "network_buffer", "stdin_buffer_size", "memory_size",
                     "network_packet_size", "interface", "port")
    parser_modifiers = {"command" : {"types" : ("positional", ),
                                     "nargs" : '?'},
                        "help" : {"types" : ("short", "long"),
                                  "nargs" : '?'}
                        }
    exit_on_help = False

    def __init__(self, **kwargs):
        self.process_requests = []
        self.connected_clients = []
        self.login_threads = []
        self.authenticate = {"root" : hash("password")}
        self.client_namespaces = {}
        self.swap_file = tempfile.TemporaryFile()
        self.log_file = open("%s.log" % self.__class__.__name__, "a")

        super(Metapython, self).__init__(**kwargs)
        """implementation = self.implementation
        if implementation != defaults.DEFAULT_IMPLEMENTATION:
            #command = sys.argv
           # command[0] = self.implementation
           command = [self.implementation, "metapython.py"] + sys.argv[1:]
           print "starting new process", command
           self.start_process(command)"""
        self.objects.setdefault(self.authentication_scheme.split(".", 1)[-1], [])
        self.network_buffer = {}
        self.setup_environment()
        self.start_interpreter()

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

    def start_interpreter(self):
        # construct a server
        # these are what the accept()-ed connection will call
        client_options = {"socket_recv" : self._socket_recv,
                          "socket_send" : self._socket_send}

        server_options = {"client_options" : client_options,
                   "on_connect" : self._on_connect,
                   "name" : self.instance_name,
                   "interface" : self.interface,
                   "port" : self.port}

        # delay until machine is running
        Instruction("Asynchronous_Network", "create", "networklibrary.Server", **server_options).execute()

        module_name = self.command.split(".py")[0]
        Instruction("Metapython", "import_module", module_name).execute()

        machine = self.create("vmlibrary.Machine")
        machine.create("networklibrary.Asynchronous_Network")
        machine.run()

    def import_module(self, module_name):
        module = __import__(module_name)

    def _on_connect(self, connection):
        self.network_buffer[connection] = ''#connection.recv(self.network_packet_size)
        options = {"handle_success" : self.handle_login_success,
                   "connection" : connection,
                   "network_buffer" : self.network_buffer,
                   "authenticate" : self.authenticate}

        Instruction("Asynchronous_Network", "add", connection).execute()
        login_thread = self.create(self.authentication_scheme, **options)

    def _socket_recv(self, connection):
        self.network_buffer[connection] = connection.recv(8096)

    def _socket_send(self, connection, data):
        connection.send(data)

    def run(self):
        self.handle_logins()

        for client in self.connected_clients:
            input = self.network_buffer[client]
            self.network_buffer[client] = ''
            if input:
                self._main(client, input)

        #for index, process in enumerate(self.process_requests):
         #   self.process_requests.remove[index]
            #utilities.shell("{0} {1}".format(*process))

        self.run_instruction.execute()

    def handle_logins(self):
        for login_thread in self.objects["Basic_Authentication"]:
            login_thread.run()

    def handle_login_success(self, connection):
        username = connection.username
        address = connection.getpeername()
        prompt = self.prompt
        string_info = (username, address,
                       sys.version, sys.platform, self.copyright,
                       self.__class__.__name__, self.implementation)
        
        response = "Welcome {0} from {1}\nPython {2} on {3}\n{4}\n{5} ({6})\n".format(*string_info)
        Instruction("Asynchronous_Network", "buffer_data", connection, response).execute()

        self.connected_clients.append(connection)
        self.network_buffer[connection] = ""

        # controls namespace that clients have access to
        
        self.client_namespaces[connection] =\
        {"__builtins__" : globals()["__builtins__"], 
         "__doc__" : globals()["__doc__"],
         "__name__" : "%s __main__" % username,
         "Instruction" : Instruction}
        
        def _globals():
            return self.client_namespaces[connection]
        self.client_namespaces["globals"] = _globals()
        
    def _main(self, connection, input):
        backup = sys.stdout
        sys.stdout = self.swap_file
        code = self._compile(input)
        if code:
            self.execute_code(connection, code)

        sys.stdout.seek(0)
        results = sys.stdout.read()
        if results:
            self.log_file.write("Results: " + results)
            Instruction("Asynchronous_Network", "buffer_data", connection, results).execute()
        sys.stdout.seek(0)
        sys.stdout.truncate() # delete contents
        sys.stdout = backup

    def _compile(self, input):
        try:
            code = codeop.compile_command(input, "<stdin>", "exec")
        except (SyntaxError, OverflowError, ValueError) as error: # did not compile
            if type(error) == SyntaxError:
                sys.stdout.write(self.traceback())
        else:
            self.log_file.write("Command:\n"+input)
            return code

    def execute_code(self, connection, code):
        _globals = self.client_namespaces[connection]
        try:
            exec code in globals(), self.client_namespaces[connection]
        except BaseException as error:
            sys.stdout = self.swap_file # can be changed by code and not changed back
            if type(error) == SystemExit:
                raise
            else:
                sys.stdout.write(self.traceback())

    def exit(self, exit_code=0):
        sys.exit(0)

    def start_process(self, sys_argvs):
        os.execlp(*sys_argvs)


if __name__ == "__main__":
    metapython = Metapython(parse_args=True, parent=__name__)
