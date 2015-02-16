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
from traceback import format_exc
from multiprocessing import cpu_count
from StringIO import StringIO

NO_ARGS = tuple()
NO_KWARGS = dict()
PROCESSOR_COUNT = 1#cpu_count()

# Base
# you can save memory if you have LOTS of objects but
# few that actually use their memory. note that for reasonable
# amounts of objects the difference is negligible and
# not worth the loss of convenience
MANUALLY_REQUEST_MEMORY = 0
DEFAULT_MEMORY_SIZE = 4096
Base = {"memory_size" : DEFAULT_MEMORY_SIZE,
"network_packet_size" : 4096,
"verbosity" : '',
"deleted" : False}

Process = Base.copy()
Process.update({"auto_start" : True,
"network_buffer" : '',
"keyboard_input" : '',
"priority" : .04})

Thread = Base.copy()

# vmlibrary

Processor = Base.copy()
Processor.update({"_cache_flush_interval" : 15})

System = Base.copy()
System.update({"name" : "system",
"status" : "",
"hardware_configuration" : tuple(),
"startup_processes" : tuple()})

Machine = Base.copy()
Machine.update({"processor_count" : PROCESSOR_COUNT,
"system_configuration" : (("vmlibrary.System", NO_ARGS, NO_KWARGS), )})

User_Input = Process.copy()

# network

Socket = Base.copy()
Socket.update({"blocking" : 0,
"timeout" : 0,
"allow_port_zero" : True,
"idle" : True,
"timeout_after" : 0,
"add_on_init" : True,
"network_packet_size" : 32768,
"memory_size" : 32768,
"network_buffer" : '',
"interface" : "0.0.0.0",
"port" : 0})

Connection = Socket.copy()
Connection.update({"socket_family" : socket.AF_INET,
"socket_type" : socket.SOCK_STREAM})

Server = Connection.copy()
Server.update({"port" : 80,
"backlog" : 50,
"name" : "",
"reuse_port" : 0,
"inbound_connection_type" : "network.Inbound_Connection",
"share_methods" : ("on_connect", "client_socket_recv", "client_socket_send")})

Udp_Socket = Socket.copy()

Outbound_Connection = Connection.copy()
Outbound_Connection.update({"ip" : "",
"port" : 80,
"target" : tuple(),
"as_port" : 0,
"connect_attempts" : 10,
"timeout_notify" : True,
"add_on_init" : False,
"bad_target_verbosity" : 0}) # alert verbosity when trying to connect to bad address
del Outbound_Connection["interface"]

Inbound_Connection = Connection.copy()

# network2
Service = Socket.copy()
Service.update({"resend_limit" : 10,
"resend_interval" : .2})

Authenticated_Service = Service.copy()
Authenticated_Service.update({"database_filename" : ":memory:",
"login_message" : 'login success'})

Authenticated_Client = Service.copy()
Authenticated_Client.update({"email" : '',
"username" : "",
"password" : ''})

Service_Listing = Service.copy()

File_Service = Service.copy()
File_Service.update({"network_packet_size" : 16384,
"mmap_threshold" : 16384,
"timeout_after" : 15})

Download = Service.copy()
Download.update({"filesize" : 0,
"filename" :'',
"filename_prefix" : "Download",
"download_in_progress" : False,
"network_packet_size" : 16384,
"timeout_after" : 15})

# only addresses in the range of 224.0.0.0 to 230.255.255.255 are valid for IP multicast
Multicast_Beacon = Udp_Socket.copy()
Multicast_Beacon.update({"packet_ttl" : struct.pack("b", 127),
"multicast_group" : "224.0.0.0",
"multicast_port" : 1929})

Multicast_Receiver = Udp_Socket.copy()
Multicast_Receiver.update({"interface" : "0.0.0.0",
"ip" : "224.0.0.0",
"port" : 0})

Basic_Authentication_Client = Thread.copy()
Basic_Authentication_Client.update({"memory_size" : 4096,
"credentials" : tuple()})

Basic_Authentication = Thread.copy()
Basic_Authentication.update({"invalid_password_string" : "Invalid Password",
"invalid_username_string" : "Invalid Username"})
Asynchronous_Network = Process.copy()

Asynchronous_Network.update({"number_of_sockets" : 0,
"priority" : .01,
"update_priority" : 5})

"""# Mail Server
Mail_Server = Process.copy()
Mail_Server.update({"address" : "notreal@inbox.com",
"mail_server_name" : "metapython_email_server"})"""

 # Metapython
JYTHON = "java -jar jython.jar"
PYPY = "pypy"
CPYTHON = "python"
DEFAULT_IMPLEMENTATION = CPYTHON

Shell_Connection = Outbound_Connection.copy()
Shell_Connection.update({"login_attempt_interval" : .05})
    
Shell = Process.copy()
Shell.update({"username" : "root",
"password" : "password",
"prompt" : ">>> ",
"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
"auto_start" : False,
"ip" : "localhost",
"port" : 40022,
"startup_definitions" : ''})

Metapython = Process.copy()
Metapython.update({"command" : "shell_launcher.py",
"implementation" : DEFAULT_IMPLEMENTATION,
"environment_setup" : ["PYSDL2_DLL_PATH = C:\\Python27\\DLLs"],
"interface" : "0.0.0.0",
"port" : 40022,
"prompt" : ">>> ",
"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
"priority" : .04,
"interpreter_enabled" : True})
#"help" : "Execute a python script or launch a live metapython session"})
