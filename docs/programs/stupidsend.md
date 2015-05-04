stupidsend
==============



_socketobject
--------------

	socket([family[, type[, proto]]]) -> socket object

Open a socket of the given type.  The family argument specifies the
address family; it defaults to AF_INET.  The type argument specifies
whether this is a stream (SOCK_STREAM, this is the default)
or datagram (SOCK_DGRAM) socket.  The protocol argument defaults to 0,
specifying the default protocol.  Keyword arguments are accepted.

A socket object represents one endpoint of a network connection.

Methods of socket objects (keyword arguments not allowed):

accept() -- accept a connection, returning new socket and client address
bind(addr) -- bind the socket to a local address
close() -- close the socket
connect(addr) -- connect the socket to a remote address
connect_ex(addr) -- connect, return an error code instead of an exception
dup() -- return a new socket object identical to the current one [*]
fileno() -- return underlying file descriptor
getpeername() -- return remote address [*]
getsockname() -- return local address
getsockopt(level, optname[, buflen]) -- get socket options
gettimeout() -- return timeout or None
listen(n) -- start listening for incoming connections
makefile([mode, [bufsize]]) -- return a file object for the socket [*]
recv(buflen[, flags]) -- receive data
recv_into(buffer[, nbytes[, flags]]) -- receive data (into a buffer)
recvfrom(buflen[, flags]) -- receive data and sender's address
recvfrom_into(buffer[, nbytes, [, flags])
  -- receive data and sender's address (into a buffer)
sendall(data[, flags]) -- send all data
send(data[, flags]) -- send data, may not send all of it
sendto(data[, flags], addr) -- send data to a given address
setblocking(0 | 1) -- set or clear the blocking I/O flag
setsockopt(level, optname, value) -- set socket options
settimeout(None | float) -- set or clear the timeout
shutdown(how) -- shut down traffic in one or both directions

 [*] not available on all platforms!


Method resolution order: 

	(<class 'socket._socketobject'>, <type 'object'>)

- **shutdown****:

		shutdown(flag)

Shut down the reading side of the socket (flag == SHUT_RD), the writing side
of the socket (flag == SHUT_WR), or both ends (flag == SHUT_RDWR).


- **gettimeout****:

		gettimeout() -> timeout

Returns the timeout in seconds (float) associated with socket 
operations. A timeout of None indicates that timeouts on socket 
operations are disabled.


- **accept**(self):

		accept() -> (socket object, address info)

Wait for an incoming connection.  Return a new socket representing the
connection, and the address of the client.  For IP sockets, the address
info is a pair (hostaddr, port).


- **connect****:

		connect(address)

Connect the socket to a remote address.  For IP sockets, the address
is a pair (host, port).


- **getsockname****:

		getsockname() -> address info

Return the address of the local endpoint.  For IP sockets, the address
info is a pair (hostaddr, port).


- **close**(self, _closedsocket, _delegate_methods, setattr):

		close()

Close the socket.  It cannot be used after this call.


- **getsockopt****:

		getsockopt(level, option[, buffersize]) -> value

Get a socket option.  See the Unix manual for level and option.
If a nonzero buffersize argument is given, the return value is a
string of that length; otherwise it is an integer.


- **connect_ex****:

		connect_ex(address) -> errno

This is like connect(address), but returns an error code (the errno value)
instead of raising an exception when an error occurs.


- **makefile**(self, mode, bufsize):

		makefile([mode[, bufsize]]) -> file object

        Return a regular file object corresponding to the socket.  The mode
        and bufsize arguments are as for the built-in open() function.


- **listen****:

		listen(backlog)

Enable a server to accept connections.  The backlog argument must be at
least 0 (if it is lower, it is set to 0); it specifies the number of
unaccepted connections that the system will allow before refusing new
connections.


- **setsockopt****:

		setsockopt(level, option, value)

Set a socket option.  See the Unix manual for level and option.
The value argument can either be an integer or a string.


- **dup**(self):

		dup() -> socket object

        Return a new socket object connected to the same system resource.


- **ioctl****:

		ioctl(cmd, option) -> long

Control the socket with WSAIoctl syscall. Currently supported 'cmd' values are
SIO_RCVALL:  'option' must be one of the socket.RCVALL_* constants.
SIO_KEEPALIVE_VALS:  'option' is a tuple of (onoff, timeout, interval).


- **getpeername****:

		getpeername() -> address info

Return the address of the remote endpoint.  For IP sockets, the address
info is a pair (hostaddr, port).


- **setblocking****:

		setblocking(flag)

Set the socket to blocking (flag is true) or non-blocking (false).
setblocking(True) is equivalent to settimeout(None);
setblocking(False) is equivalent to settimeout(0.0).


- **fileno****:

		fileno() -> integer

Return the integer file descriptor of the socket.


- **bind****:

		bind(address)

Bind the socket to a local address.  For IP sockets, the address is a
pair (host, port); the host must refer to the local host. For raw packet
sockets the address is a tuple (ifname, proto [,pkttype [,hatype]])


- **sendall****:

		sendall(data[, flags])

Send a data string to the socket.  For the optional flags
argument, see the Unix manual.  This calls send() repeatedly
until all data is sent.  If an error occurs, it's impossible
to tell how much data has been sent.


- **settimeout****:

		settimeout(timeout)

Set a timeout on socket operations.  'timeout' can be a float,
giving in seconds, or None.  Setting a timeout of None disables
the timeout feature and is equivalent to setblocking(1).
Setting a timeout of zero is the same as setblocking(0).


- **create_connection**(address, timeout, source_address):

		Connect to *address* and return the socket object.

    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) and return the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* is supplied, the
    global default timeout setting returned by :func:`getdefaulttimeout`
    is used.  If *source_address* is set it must be a tuple of (host, port)
    for the socket to bind as a source address before making the connection.
    An host of '' or port 0 tells the OS to use the default.
    


error
--------------

	No documentation available


Method resolution order: 

	(<class 'socket.error'>,
	 <type 'exceptions.IOError'>,
	 <type 'exceptions.EnvironmentError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

gaierror
--------------

	No documentation available


Method resolution order: 

	(<class 'socket.gaierror'>,
	 <class 'socket.error'>,
	 <type 'exceptions.IOError'>,
	 <type 'exceptions.EnvironmentError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

- **getfqdn**(name):

		Get fully qualified domain name from name.

    An empty argument is interpreted as meaning the local host.

    First the hostname returned by gethostbyaddr() is checked, then
    possibly existing aliases. In case no FQDN is available, hostname
    from gethostname() is returned.
    


herror
--------------

	No documentation available


Method resolution order: 

	(<class 'socket.herror'>,
	 <class 'socket.error'>,
	 <type 'exceptions.IOError'>,
	 <type 'exceptions.EnvironmentError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

_socketobject
--------------

	socket([family[, type[, proto]]]) -> socket object

Open a socket of the given type.  The family argument specifies the
address family; it defaults to AF_INET.  The type argument specifies
whether this is a stream (SOCK_STREAM, this is the default)
or datagram (SOCK_DGRAM) socket.  The protocol argument defaults to 0,
specifying the default protocol.  Keyword arguments are accepted.

A socket object represents one endpoint of a network connection.

Methods of socket objects (keyword arguments not allowed):

accept() -- accept a connection, returning new socket and client address
bind(addr) -- bind the socket to a local address
close() -- close the socket
connect(addr) -- connect the socket to a remote address
connect_ex(addr) -- connect, return an error code instead of an exception
dup() -- return a new socket object identical to the current one [*]
fileno() -- return underlying file descriptor
getpeername() -- return remote address [*]
getsockname() -- return local address
getsockopt(level, optname[, buflen]) -- get socket options
gettimeout() -- return timeout or None
listen(n) -- start listening for incoming connections
makefile([mode, [bufsize]]) -- return a file object for the socket [*]
recv(buflen[, flags]) -- receive data
recv_into(buffer[, nbytes[, flags]]) -- receive data (into a buffer)
recvfrom(buflen[, flags]) -- receive data and sender's address
recvfrom_into(buffer[, nbytes, [, flags])
  -- receive data and sender's address (into a buffer)
sendall(data[, flags]) -- send all data
send(data[, flags]) -- send data, may not send all of it
sendto(data[, flags], addr) -- send data to a given address
setblocking(0 | 1) -- set or clear the blocking I/O flag
setsockopt(level, optname, value) -- set socket options
settimeout(None | float) -- set or clear the timeout
shutdown(how) -- shut down traffic in one or both directions

 [*] not available on all platforms!


Method resolution order: 

	(<class 'socket._socketobject'>, <type 'object'>)

- **shutdown****:

		shutdown(flag)

Shut down the reading side of the socket (flag == SHUT_RD), the writing side
of the socket (flag == SHUT_WR), or both ends (flag == SHUT_RDWR).


- **gettimeout****:

		gettimeout() -> timeout

Returns the timeout in seconds (float) associated with socket 
operations. A timeout of None indicates that timeouts on socket 
operations are disabled.


- **accept**(self):

		accept() -> (socket object, address info)

Wait for an incoming connection.  Return a new socket representing the
connection, and the address of the client.  For IP sockets, the address
info is a pair (hostaddr, port).


- **connect****:

		connect(address)

Connect the socket to a remote address.  For IP sockets, the address
is a pair (host, port).


- **getsockname****:

		getsockname() -> address info

Return the address of the local endpoint.  For IP sockets, the address
info is a pair (hostaddr, port).


- **close**(self, _closedsocket, _delegate_methods, setattr):

		close()

Close the socket.  It cannot be used after this call.


- **getsockopt****:

		getsockopt(level, option[, buffersize]) -> value

Get a socket option.  See the Unix manual for level and option.
If a nonzero buffersize argument is given, the return value is a
string of that length; otherwise it is an integer.


- **connect_ex****:

		connect_ex(address) -> errno

This is like connect(address), but returns an error code (the errno value)
instead of raising an exception when an error occurs.


- **makefile**(self, mode, bufsize):

		makefile([mode[, bufsize]]) -> file object

        Return a regular file object corresponding to the socket.  The mode
        and bufsize arguments are as for the built-in open() function.


- **listen****:

		listen(backlog)

Enable a server to accept connections.  The backlog argument must be at
least 0 (if it is lower, it is set to 0); it specifies the number of
unaccepted connections that the system will allow before refusing new
connections.


- **setsockopt****:

		setsockopt(level, option, value)

Set a socket option.  See the Unix manual for level and option.
The value argument can either be an integer or a string.


- **dup**(self):

		dup() -> socket object

        Return a new socket object connected to the same system resource.


- **ioctl****:

		ioctl(cmd, option) -> long

Control the socket with WSAIoctl syscall. Currently supported 'cmd' values are
SIO_RCVALL:  'option' must be one of the socket.RCVALL_* constants.
SIO_KEEPALIVE_VALS:  'option' is a tuple of (onoff, timeout, interval).


- **getpeername****:

		getpeername() -> address info

Return the address of the remote endpoint.  For IP sockets, the address
info is a pair (hostaddr, port).


- **setblocking****:

		setblocking(flag)

Set the socket to blocking (flag is true) or non-blocking (false).
setblocking(True) is equivalent to settimeout(None);
setblocking(False) is equivalent to settimeout(0.0).


- **fileno****:

		fileno() -> integer

Return the integer file descriptor of the socket.


- **bind****:

		bind(address)

Bind the socket to a local address.  For IP sockets, the address is a
pair (host, port); the host must refer to the local host. For raw packet
sockets the address is a tuple (ifname, proto [,pkttype [,hatype]])


- **sendall****:

		sendall(data[, flags])

Send a data string to the socket.  For the optional flags
argument, see the Unix manual.  This calls send() repeatedly
until all data is sent.  If an error occurs, it's impossible
to tell how much data has been sent.


- **settimeout****:

		settimeout(timeout)

Set a timeout on socket operations.  'timeout' can be a float,
giving in seconds, or None.  Setting a timeout of None disables
the timeout feature and is equivalent to setblocking(1).
Setting a timeout of zero is the same as setblocking(0).


timeout
--------------

	No documentation available


Method resolution order: 

	(<class 'socket.timeout'>,
	 <class 'socket.error'>,
	 <type 'exceptions.IOError'>,
	 <type 'exceptions.EnvironmentError'>,
	 <type 'exceptions.StandardError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)