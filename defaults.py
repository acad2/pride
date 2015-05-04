#   mpf.defaults - config file - contains attributes:values for new instances

import struct
import socket
import os

NO_ARGS = tuple()
NO_KWARGS = dict()

if "__file__" not in globals():
    FILEPATH = os.getcwd()
else:
    FILEPATH = os.path.split(__file__)[0]

# Base
Base = {"verbosity" : '',
"_deleted" : False,
"replace_reference_on_load" : True}

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
"socket_family" : socket.AF_INET,
"socket_type" : socket.SOCK_STREAM,
"protocol" : socket.IPPROTO_IP,
"network_buffer" : '',
"interface" : "0.0.0.0",
"port" : 0,
"connection_attempts" : 10,
"bind_on_init" : False,
"closed" : False,
"_connecting" : False,
"added_to_network" : False})

Raw_Socket = Socket.copy()
Raw_Socket.update({"socket_type" : socket.SOCK_RAW})
                   
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
"startup_components" : ("mpre.fileio.File_System", "vmlibrary.Processor",
                        "mpre._metapython.Alert_Handler", "mpre.userinput.User_Input",
                        "mpre.network.Network", "mpre.network2.RPC_Handler"),
"interface" : "0.0.0.0",
"port" : 40022,
"prompt" : ">>> ",
"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.',
"interpreter_enabled" : True,
"startup_definitions" : ''})
#"help" : "Execute a python script or launch a live metapython session"})

# fileio

File_Object = Base.copy()
File_Object.update({"path" : '',
                    "file_system" : "disk",
                    "directory" : None,
                    "is_directory" : False})
                    
Directory = File_Object.copy()
Directory.update({"is_directory" : True})

File = File_Object.copy()
File.update({"file" : None,
             "file_type" : "StringIO.StringIO",
             "mode" : ""})

Encrypted_File = File.copy()
Encrypted_File.update({"block_size" : 1024})
             
File_System = Process.copy()
File_System.update({"file_systems" : ("disk", "virtual"),
                    "auto_start" : False})             
  
Package = Base.copy()
Package.update({"python_extensions" : (".py", ".pyx", ".pyd", ".pso", ".so"),
                "package_name" : None,
                "include_all_source" : True,
                "replace_reference_on_load" : False,
                "include_documentation" : False,
                "top_level_package" : ''})  
                
Loader = Base.copy()
Loader.update({"required_imports" : ("sys", "hashlib", "pickle", "importlib", "types"),
               "embedded_objects" : ("mpre.utilities.load", "mpre.errors.CorruptPickleError",
                                     "mpre.module_utilities.create_module"),
               "importer" : "mpre.package.Package_Importer"})
                
Executable = Base.copy()                    
Executable.update({"filename" : "metapython.exe",
                   "package" : None,
                   "file" : None,
                   "loader_type" : "mpre.programs.buildlauncher.Loader",
                   "main_source" : ''})                    