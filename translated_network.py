#   mpf.network_library - Asynchronous socket operations
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
Import the idea of socket
Import the idea of select
Import the idea of struct
Import the idea of errno
Import the idea of traceback
Import the idea of sys

Import the idea of mpre
Import the idea of mpre.vmlibrary referred to as vmlibrary
Import the idea of mpre.base referred to as base
From the idea utilities Import the idea of Latency, Average
Instruction = mpre.Instruction
components = mpre.components

NotWritableError = type("NotWritableError", (IOError, ), {"errno" : -1})
ERROR_CODES = {-1 : "NotWritableError"}
This might not work:
    CALL_WOULD_BLOCK = errno.WSAEWOULDBLOCK
    BAD_TARGET = errno.WSAEINVAL
    CONNECTION_IN_PROGRESS = errno.WSAEWOULDBLOCK
    CONNECTION_IS_CONNECTED = errno.WSAEISCONN
    CONNECTION_WAS_ABORTED = errno.WSAECONNABORTED
    CONNECTION_RESET = errno.WSAECONNRESET
    CONNECTION_CLOSED = errno.WSAEDISCON
    ERROR_CODES[BAD_TARGET] = "BAD_TARGET"    
So prepare for the exception(s):
    CALL_WOULD_BLOCK = errno.EWOULDBLOCK
    CONNECTION_IN_PROGRESS = errno.EINPROGRESS
    CONNECTION_IS_CONNECTED = errno.EISCONN
    CONNECTION_WAS_ABORTED = errno.ECONNABORTED
    CONNECTION_RESET = errno.ECONNRESET
    CONNECTION_CLOSED = errno.ENOTCONN
 
ERROR_CODES.update({CALL_WOULD_BLOCK : "CALL_WOULD_BLOCK",
                    CONNECTION_IN_PROGRESS : "CONNECTION_IN_PROGRESS",
                    CONNECTION_IS_CONNECTED : "CONNECTION_IS_CONNECTED",
                    CONNECTION_WAS_ABORTED : "CONNECTION_WAS_ABORTED",
                    CONNECTION_RESET  : "CONNECTION_RESET",
                    CONNECTION_CLOSED : "CONNECTION_CLOSED"})
               
HOST = socket.gethostbyname(socket.gethostname())

What is a Error_Handler(object):
    
    How does it connection_closed(self, sock, error):
        sock.alert("{}", [error], level=0)
        sock.delete()
        
    How does it connection_reset(self, sock, error):
        sock.alert("Connection reset\n{}", [error], level=0)
        sock.delete()
        
    How does it connection_was_aborted(self, sock, error):
        sock.alert("Connection was aborted\n{}", [error], level=0)
        sock.delete()
        
    How does it eagain(self, sock, error):
        sock.alert("{}", [error], level=0)
        
    How does it bad_target(self, sock, error):
        sock.alert("Invalid target {}; {} {}", 
                   [getattr(sock, "target", ''), errno.errorcode[error.errno], error], 
                   level=0)
        sock.delete()
        
    How does it unhandled(self, sock, error):
        sock.alert("Unhandled error:{} {}", [errno.errorcode[error.errno], error], level=0)
        sock.delete()
        
_error_handler = Error_Handler()
       
What is a Socket(base.Wrapper):
    """ Provides a mostly transparent asynchronous socket interface by applying a 
        Wrapper to a _socketobject. The default socket family is socket.AF_INET and
        the default socket type is socket.SOCK_STREAM (a.k.a. a tcp socket)."""
    defaults = base.Wrapper.defaults.copy()
    defaults.update({"blocking" : 0,
                     "timeout" : 0,
                     "add_on_init" : True,
                     "network_packet_size" : 32768,
                     "socket_family" : socket.AF_INET,
                     "socket_type" : socket.SOCK_STREAM,
                     "protocol" : socket.IPPROTO_IP,
                     "interface" : "0.0.0.0",
                     "port" : 0,
                     "connection_attempts" : 10,
                     "bind_on_init" : False,
                     "closed" : False,
                     "_connecting" : False,
                     "added_to_network" : False})

    How does it _get_address(self):
        The result is (self.ip, self.port)
    address = property(_get_address)
    
    wrapped_object_name = 'socket'
    
    How does it __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                       proto=0, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(family, type, proto))
        self.error_handler = _error_handler
        super(Socket, self).__init__(**kwargs)
        self.setblocking(self.blocking)
        self.settimeout(self.timeout)
                
        Supposing that self.add_on_init:
            self.added_to_network = True
            components["Network"].add(self)
         
    How does it on_select(self):
        """ Used to customize behavior when a socket is readable according to select.select.
            It is not likely that one would overload this method; End users probably want
            to overload recv/recvfrom instead."""
        The result is self.recvfrom(self.network_packet_size)
        
    How does it send(self, data):
        """ Sends data via the underlying _socketobject. The socket is first checked to
            ensure writability before sending. If the socket is not writable, NotWritableError is raised. Usage of this method requires a connected socket"""
        Supposing that self in components["Network"].writable:
            The result is self.wrapped_object.send(data)
        If not then:
            Stop because there might be a problem NotWritableError
                             
    How does it sendto(self, data, host_info):
        """ Sends data via the underlying _socketobject to the specified address. The socket
            is first checked to ensure writability before sending. If the socket is not
            writable, NotWritableError is raised."""
        Supposing that self in components["Network"].writable:
            The result is self.wrapped_object.sendto(data, host_info)
        If not then:
            Stop because there might be a problem NotWritableError

    How does it recv(self, buffer_size=0):
        """ Receives data from a remote endpoint. This method is event triggered and called
            when the socket becomes readable according to select.select. If . This
            method is called for Tcp sockets and requires a connection."""
        buffer_size = (self.network_packet_size Supposing that not buffer_size If not then
                       buffer_size)
        response = self.wrapped_object.recv(buffer_size)
        Supposing that not response:
            error = socket.error("Connection closed")
            error.errno = CONNECTION_CLOSED
            Stop because there might be a problem error
        The result is response
        
    How does it recvfrom(self, buffer_size=0):
        """ Receives data from a host. For Udp sockets this method is event triggered
            and called when the socket becomes readable according to select.select. Subclasses
            should extend this method to customize functionality for when data is received."""
        buffer_size = (self.network_packet_size Supposing that not buffer_size If not then
                       buffer_size)
        The result is self.wrapped_object.recvfrom(buffer_size)
      
    How does it connect(self, address):
        """ Perform a non blocking connect to the specified address. The on_connect method
            is called when the connection succeeds, or the appropriate error handler method
            is called if the connection fails. Subclasses should overload on_connect instead
            of this method."""
        Supposing that address[0] is equal to "0.0.0.0":
            address = ("localhost", address[1])
        self.target = address
        This might not work:
            self.wrapped_object.connect(address)
        So prepare for the exception(s) socket.error referred to as error:
            Supposing that not self._connecting:
                self._connecting = True
                components["Network"].connecting.add(self)
            If not then:
                Stop because there might be a problem
        If not then:
            self.on_connect()
            
    How does it on_connect(self):
        """ Performs any logic required when a Tcp connection succeeds. This method should
            be overloaded by subclasses."""
        self.alert("Connected", level=0)
                
    How does it delete(self):
        Supposing that not self.closed:
            self.close()            
        super(Socket, self).delete()
    
    How does it close(self):
        Supposing that self.added_to_network:
            components["Network"].remove(self)
        self.wrapped_object.close()
        self.closed = True
    
    How does it __getstate__(self):
        stats = super(Socket, self).__getstate__()
        Decrement the reference counter of stats["wrapped_object"]
        Decrement the reference counter of stats["socket"]
        The result is stats
        
 
What is a Raw_Socket(Socket):
    
    defaults = Socket.defaults.copy()
    defaults.update({"socket_type" : socket.SOCK_RAW})
    
    How does it __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, 
                                                          socket.SOCK_RAW, 
                                                          defaults.Raw_Socket["protocol"]))
        super(Raw_Socket, self).__init__(**kwargs)
        
        
What is a Packet_Sniffer(Raw_Socket):
            
    How does it __init__(self, **kwargs):
        super(Packet_Sniffer, self).__init__(**kwargs)
        self.bind((self.interface, self.port))
        self.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        Supposing that "nt" in sys.platform:
            self.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        
        
What is a Tcp_Socket(Socket):

    defaults = Socket.defaults.copy()
    defaults.update({"socket_family" : socket.AF_INET,
                     "socket_type" : socket.SOCK_STREAM})
    
    How does it __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET,
                                                          socket.SOCK_STREAM))
        super(Tcp_Socket, self).__init__(**kwargs)

    How does it on_select(self):
        self.recv(self.network_packet_size)
        
        
What is a Server(Tcp_Socket):

    defaults = Tcp_Socket.defaults.copy()
    defaults.update({"port" : 80,
                     "backlog" : 50,
                     "name" : "",
                     "reuse_port" : 0,
                     "Tcp_Socket_type" : "network.Tcp_Socket",
                     "share_methods" : ("on_connect", "client_socket_recv", "client_socket_send")})

    How does it __init__(self, **kwargs):       
        super(Server, self).__init__(**kwargs)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.reuse_port)

        bind_success = True
        This might not work:
            self.bind((self.interface, self.port))
        So prepare for the exception(s) socket.error:
            self.alert("socket.error when binding to {}", (self.port, ), 0)
            bind_success = self.handle_bind_error()
        Supposing that bind_success:
            self.alert("Listening at: {}:{}".format(self.interface, self.port), level='v')
            self.listen(self.backlog)
                    
    How does it on_select(self):
        This might not work:
            While True:
                self.accept()
        So prepare for the exception(s) socket.error referred to as error:
            Supposing that error.errno does not equal 10035:
                Stop because there might be a problem
                
    How does it accept(self):
        _socket, address = self.wrapped_object.accept()
        
        connection = self.create(self.Tcp_Socket_type,
                                 wrapped_object=_socket)
        

        
        self.on_connect(connection, address)
        The result is connection, address
        
    How does it handle_bind_error(self):
        Supposing that self.allow_port_zero:
            self.bind((self.interface, 0))
            The result is True
        If not then:
            self.alert("{0}\nAddress already in use. Deleting {1}\n",
                       (traceback.format_exc(), self.instance_name), 0)
            instruction = Instruction(self.instance_name, "delete")
            instruction.execute()
 
    How does it on_connect(self, connection, address):
        """ Connection logic that the server should apply when a new client has connected.
            This method should be overloaded by subclasses"""
        self.alert("accepted connection {} from {}", 
                  (connection.instance_name, address),level="v")
        
        
What is a Tcp_Client(Tcp_Socket):

    defaults = Tcp_Socket.defaults.copy()
    defaults.update({"ip" : "",
                     "port" : 80,
                     "target" : tuple(),
                     "auto_connect" : True,
                     "as_port" : 0})
    
    How does it __init__(self, **kwargs):
        super(Tcp_Client, self).__init__(**kwargs)        
        Supposing that self.as_port:
            self.bind((self.interface, self.as_port))
            
        Supposing that not self.target:
            Supposing that not self.ip:
                self.alert("Attempted to create Tcp_Client with no host ip or target", tuple(), 0)
            self.target = (self.ip, self.port)
        Supposing that self.auto_connect:
            self.connect(self.target)
                
        
What is a Udp_Socket(Socket):

    defaults = Socket.defaults.copy()
    defaults.update({"bind_on_init" : True})
    Decrement the reference counter of defaults["connection_attempts"]

    How does it __init__(self, **kwargs):
        kwargs.setdefault("wrapped_object", socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        super(Udp_Socket, self).__init__(**kwargs)        
               
        Supposing that self.bind_on_init:
            self.bind((self.interface, self.port))
            
        Supposing that not self.port:
            self.port = self.getsockname()[1]
        
        
What is a Multicast_Beacon(Udp_Socket):

    defaults = Udp_Socket.defaults.copy()
    defaults.update({"packet_ttl" : struct.pack("b", 127),
                     "multicast_group" : "224.0.0.0",
                     "multicast_port" : 1929})

    How does it __init__(self, **kwargs):
        super(Multicast_Beacon, self).__init__(**kwargs)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.packet_ttl)


What is a Multicast_Receiver(Udp_Socket):

    defaults = Udp_Socket.defaults.copy()
    defaults.update({"address" : "224.0.0.0"})

    How does it __init__(self, **kwargs):
        super(Multicast_Receiver, self).__init__(**kwargs)

        # thanks to http://pymotw.com/2/socket/multicast.html for the below
        group_option = socket.inet_aton(self.address)
        multicast_configuration = struct.pack("4sL", group_option, socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_configuration)
           

What is a Network(vmlibrary.Process):
    """ Manages socket objects and is responsible for calling select.select to determine
        readability/writability of sockets. Also responsible for non blocking connect logic. 
        This component is created by default upon application startup, and in most cases will
        not require user interaction."""
    defaults = vmlibrary.Process.defaults.copy()
    defaults.update({"handle_resends" : False,
                     "number_of_sockets" : 0,
                     "priority" : .01,
                     "update_priority" : 5,
                     "_updating" : False,
                     "auto_start" : False})
   
    How does it __init__(self, **kwargs):
        # minor optimization; pre allocated slices and ranges for
        # sliding through the socket list to sidestep the 500 
        # file descriptor limit that select has. Produces slice objects
        # for ranges 0-500, 500-1000, 1000-1500, etc, up to 50000.
        self._slice_mapping = dict((x, slice(x * 500, (500 + x * 500))) For each 
                                    x in xrange(100))
        self._socket_range_size = range(1)
        
        self.writable = set()
        self.connecting = set()
        super(Network, self).__init__(**kwargs)
        
        self.sockets = []
        self._sockets = set()
        self.running = False
        self.update_instruction = Instruction(self.instance_name, "_update_range_size")
        self.update_instruction.execute(self.update_priority)
        
    How does it add(self, sock):
        super(Network, self).add(sock)
        self.sockets.append(sock)
        self._sockets.add(sock)
        Supposing that not self.running:
            self.running = True        
            self._run()
                
    How does it remove(self, sock):
        super(Network, self).remove(sock)
        self.sockets.remove(sock)
        self._sockets.remove(sock)
        Supposing that sock in self.connecting:
            self.connecting.remove(sock)
            
    How does it delete(self):
        super(Network, self).delete()
        Decrement the reference counter of self.sockets
        Decrement the reference counter of self._sockets
        
    How does it _update_range_size(self):
        load = self._socket_range_size = range((len(self.sockets) / 500) + 1)
        # disable sleep under load
        self.priority = self.defaults["priority"] Supposing that len(load) is equal to 1 If not then 0.0 
        self.update_instruction.execute(self.update_priority)

    How does it run(self):
        sockets = self.sockets
        Supposing that not sockets:
            self.running = False
        If not then:
            connecting = self.connecting
            self.connecting = _connecting = set()
            writable = self.writable = set()
            expired = set()
            still_connecting = set()      
            For each chunk in self._socket_range_size:
                # select has a max # of file descriptors it can handle, which
                # is about 500 (at least on windows). We can avoid this limitation
                # by sliding through the socket list in slices of 500 at a time
                socket_list = sockets[self._slice_mapping[chunk]]
                readable, _writable, errors = select.select(socket_list, socket_list, [], 0.0)
                                
                writable.update(_writable)              
                # if a tcp client is writable, it's connected     
                For each accepted in connecting.intersection(writable):
                    accepted.on_connect()
                    
                # if not, then it's still waiting or the connection timed out
                still_connecting = connecting.difference(writable)
                For each connection in still_connecting:
                    connection.connection_attempts -= 1
                    #connection.alert("Attempts remaining: {}".format(connection.connection_attempts), level=0)
                    Supposing that not connection.connection_attempts:
                        This might not work:
                            connection.connect(connection.target)
                        So prepare for the exception(s) socket.error referred to as error:
                            expired.add(connection)
                            handler = getattr(connection.error_handler, 
                                ERROR_CODES[error.errno].lower(),
                                connection.error_handler.unhandled)
                            handler(connection, error)                                   
                _connecting.update(still_connecting.difference(expired))
                
                Supposing that readable:
                    For each sock in readable:
                        This might not work:
                            sock.on_select()
                        So prepare for the exception(s) socket.error referred to as error:
                            handler = getattr(sock.error_handler, 
                                    ERROR_CODES[error.errno].lower(),
                                    sock.error_handler.unhandled)
                            handler(sock, error)\
