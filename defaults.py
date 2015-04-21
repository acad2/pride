#   mpf.defaults - config file - contains attributes:values for new instances
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
import struct
import socket
import os

NO_ARGS = tuple()
NO_KWARGS = dict()
FILEPATH = os.path.split(__file__)[0]

# Base
MANUALLY_REQUEST_MEMORY = 0
DEFAULT_MEMORY_SIZE = 4096

# anonymous memory passes -1  as the file descriptor to pythons mmap.mmap.
# persistent memory opens the file instance.instance_name and opens an
# mmap.mmap with that files file descriptor
ANONYMOUS = -1
PERSISTENT = 0
Base = {"memory_size" : DEFAULT_MEMORY_SIZE,
"memory_mode" : ANONYMOUS,
"verbosity" : '',
"deleted" : False}

Reactor = Base.copy()

Process = Base.copy()
Process.update({"auto_start" : True,
"priority" : .04})

# vmlibrary

Processor = Process.copy()
Processor.update({"running" : True,
"auto_start" : False})

User_Input = Process.copy()

# network

Socket = Base.copy()
Socket.update({"blocking" : 0,
"timeout" : 0,
"add_on_init" : True,
"network_packet_size" : 32768,
"memory_size" : 0,
"network_buffer" : '',
"interface" : "0.0.0.0",
"port" : 0,
"connection_attempts" : 10,
"bind_on_init" : False,
"closed" : False,
"_connecting" : False,
"added_to_network" : False})

Tcp_Socket = Socket.copy()
Tcp_Socket.update({"socket_family" : socket.AF_INET,
"socket_type" : socket.SOCK_STREAM})

Server = Tcp_Socket.copy()
Server.update({"port" : 80,
"backlog" : 50,
"name" : "",
"reuse_port" : 0,
"Tcp_Socket_type" : "network.Tcp_Socket",
"share_methods" : ("on_connect", "client_socket_recv", "client_socket_send")})

Tcp_Client = Tcp_Socket.copy()
Tcp_Client.update({"ip" : "",
"port" : 80,
"target" : tuple(),
"as_port" : 0,
"timeout_notify" : True,
"auto_connect" : True,
"bad_target_verbosity" : 0}) # alert verbosity when trying to connect to bad address
del Tcp_Client["interface"]

Udp_Socket = Socket.copy()
Udp_Socket.update({"bind_on_init" : True})
del Udp_Socket["connection_attempts"]

# only addresses in the range of 224.0.0.0 to 230.255.255.255 are valid for IP multicast
Multicast_Beacon = Udp_Socket.copy()
Multicast_Beacon.update({"packet_ttl" : struct.pack("b", 127),
"multicast_group" : "224.0.0.0",
"multicast_port" : 1929})

Multicast_Receiver = Udp_Socket.copy()
Multicast_Receiver.update({"address" : "224.0.0.0"})

Connection_Manager = Process.copy()
Connection_Manager.update({"auto_start" : False})

Network = Process.copy()
Network.update({"handle_resends" : False,
"number_of_sockets" : 0,
"priority" : .01,
"update_priority" : 5,
"_updating" : False,
"auto_start" : False})

# network2
Network_Service = Udp_Socket.copy()

Authenticated_Service = Base.copy()
Authenticated_Service.update({"database_filename" : ":memory:",
"login_message" : 'login success',
"hash_rounds" : 100000})

Authenticated_Client = Base.copy()
Authenticated_Client.update({"email" : '',
"username" : "",
"password" : '',
"target" : "Authenticated_Service"})

File_Service = Base.copy()
File_Service.update({"network_packet_size" : 16384,
"mmap_threshold" : 16384,
"timeout_after" : 15})

Download = Base.copy()
Download.update({"filesize" : 0,
"filename" :'',
"filename_prefix" : "Download",
"download_in_progress" : False,
"network_packet_size" : 16384,
"timeout_after" : 15})

 # Metapython
JYTHON = "java -jar jython.jar"
PYPY = "pypy"
CPYTHON = "python"
DEFAULT_IMPLEMENTATION = CPYTHON

Shell = Authenticated_Client.copy()
Shell.update({"email" : '',
"username" : "root",
"password" : "password",
"prompt" : ">>> ",
"startup_definitions" : '',
"target" : "Interpreter_Service"})

Interpreter_Service = Authenticated_Service.copy()
Interpreter_Service.update({"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.'})

Alert_Handler = Reactor.copy()
Alert_Handler.update({"log_level" : 0,
                      "print_level" : 0,
                      "log_name" : "Alerts.log"})
                      
Metapython = Reactor.copy()
Metapython.update({"command" : os.path.join(FILEPATH, "shell_launcher.py"),
"implementation" : DEFAULT_IMPLEMENTATION,
"environment_setup" : ["PYSDL2_DLL_PATH = C:\\Python27\\DLLs"],
"interface" : "0.0.0.0",
"port" : 40022,
"prompt" : ">>> ",
"_suspended_file_name" : "suspended_interpreter.bin",
"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
"priority" : .04,
"interpreter_enabled" : True,
"startup_definitions" : \
"""Instruction('Metapython', 'create', 'userinput.User_Input').execute()
Instruction("Metapython", "create", "network.Network").execute()
Instruction("Network", "_update_range_size").execute()"""})
#"help" : "Execute a python script or launch a live metapython session"})
