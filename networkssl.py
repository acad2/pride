import sys
import os
import ssl

import mpre.base
import mpre.network
import mpre.utilities
import mpre.userinput

SSL_DEFAULTS = {"keyfile" : None, 
                "certfile" : None, 
                "server_side" : False, 
                "cert_reqs" : ssl.CERT_NONE, 
                "ssl_version" : ssl.PROTOCOL_SSLv23, 
                "ca_certs" : None, 
                "do_handshake_on_connect" : False,
                "suppress_ragged_eofs" : True, 
                "ciphers" : None,
                "ssl_authenticated" : False,
                "dont_save" : True}
                
WRAP_SOCKET_OPTIONS = ("keyfile", "certfile", "server_side", "cert_reqs", 
                       "ssl_version", "ca_certs", "do_handshake_on_connect", 
                       "suppress_ragged_eofs", "ciphers")   

DEFAULT_CLIENT_CONTEXT = ssl.create_default_context()
DEFAULT_SERVER_CONTEXT = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                       
def generate_self_signed_certificate(name=""): # to do: pass in ssl commands and arguments
    """ Creates a name.key, name.csr, and name.crt file. These files can
        be used for the keyfile and certfile options for an ssl server socket"""
    name = name or mpre.userinput.get_user_input("Please provide the name for the .key, .crt, and .csr files: ")
    openssl = r"C:\\OpenSSL-Win32\\bin\\openssl" if 'win' in sys.platform else "openssl"
    delete_program = "del" if openssl == r"C:\\OpenSSL-Win32\\bin\\openssl" else "rm" # rm on linux, del on windows
    shell = mpre.utilities.shell
    
    shell("{} genrsa -aes256 -passout pass:x -out {}.pass.key 2048".format(openssl, name))
    shell("{} rsa -passin pass:x -in {}.pass.key -out {}.key".format(openssl, name, name))
    shell("{} req -new -key {}.key -out {}.csr".format(openssl, name, name))
    shell("{} x509 -req -days 365 -in {}.csr -signkey {}.key -out {}.crt".format(openssl, name, name, name))
    shell("{} {}.pass.key".format(delete_program, name), True)
        
class SSL_Client(mpre.network.Tcp_Client):
    
    """ An asynchronous client side Tcp socket wrapped in an ssl socket.
        Users should extend on_authentication instead of on_connect to
        initiate data transfer; on_connect is used to start the
        ssl handshake"""
    defaults = mpre.network.Tcp_Client.defaults.copy()
    defaults.update(SSL_DEFAULTS)    
    
    def __init__(self, **kwargs):        
        super(SSL_Client, self).__init__(**kwargs)
        
    def on_connect(self):
        super(SSL_Client, self).on_connect()
        self.ssl_socket = ssl.wrap_socket(self.socket, **dict((attribute, getattr(self, attribute)) 
                                                               for attribute in WRAP_SOCKET_OPTIONS))
        self.ssl_connect()
        
    def ssl_connect(self):
        try:
            self.ssl_socket.do_handshake()
        except ssl.SSLError as error:
            if error.errno != ssl.SSL_ERROR_WANT_READ:
                raise
        else:
            self.ssl_authenticated = True
            self.on_authentication()    
            
    def on_select(self):
        if self.connected and not self.ssl_authenticated:
            self.ssl_connect()
        else:
            super(SSL_Client, self).on_select()
                        
    def on_authentication(self):
        self.alert("Authenticated", level=0)
            
        
class SSL_Socket(mpre.network.Tcp_Socket):
    
    """ An asynchronous server side client socket wrapped in an ssl socket.
        Users should override the on_authentication method instead of
        on_connect"""
        
    defaults = mpre.network.Tcp_Socket.defaults.copy()
    defaults.update(SSL_DEFAULTS)
    defaults.update({"server_side" : True,
                     "certfile" : "",
                     "keyfile" : ""})
    
    def __init__(self, **kwargs):
        super(SSL_Socket, self).__init__(**kwargs)
        self.ssl_socket = ssl.wrap_socket(self.socket, **dict((attribute, getattr(self, attribute)) 
                                                               for attribute in WRAP_SOCKET_OPTIONS))
                                                               
    def on_connect(self):
        self.ssl_connect()
        
    def on_select(self):
        if not self.ssl_authenticated:
            self.ssl_connect()
        else:
            super(SSL_Socket, self).on_select()
            
    def ssl_connect(self):
        try:
            self.ssl_socket.do_handshake()
        except ssl.SSLError as error:
            if error.errno != ssl.SSL_ERROR_WANT_READ:
                raise
        else:
            self.ssl_authenticated = True
            self.on_authentication()
            
    def on_authentication(self):
        self.alert("Authenticated", level='v')
                
        
class SSL_Server(mpre.network.Server):
    
    defaults = mpre.network.Server.defaults.copy()
    defaults.update(SSL_DEFAULTS)
    defaults.update({"port" : 443,
                     "Tcp_Socket_type" : "mpre.networkssl.SSL_Socket"})       