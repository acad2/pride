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
                "ssl_authenticated" : False}
                
WRAP_SOCKET_OPTIONS = ("keyfile", "certfile", "server_side", "cert_reqs", 
                       "ssl_version", "ca_certs", "do_handshake_on_connect", 
                       "suppress_ragged_eofs", "ciphers")   

def generate_self_signed_certificate(name="server"):
    openssl = r"C:\\OpenSSL-Win32\\bin\\openssl" if 'win' in sys.platform else "openssl"
    delete_program = "rm" if openssl == "openssl" else "del" # rm on linux, del on windows
    shell = mpre.utilities.shell
    
    shell("{} genrsa -aes256 -passout pass:x -out {}.pass.key 2048".format(openssl, name))
    shell("{} rsa -passin pass:x -in {}.pass.key -out {}.key".format(openssl, name, name))
    shell("{} req -new -key {}.key -out {}.csr".format(openssl, name, name))
    shell("{} x509 -req -days 365 -in {}.csr -signkey {}.key -out {}.crt".format(openssl, name, name, name))
    shell("{} {}.pass.key".format(delete_program, name), True)
        
class SSL_Error_Handler(mpre.network.Error_Handler):
    
    def ssl_error_ssl(self, _socket, error):
        _socket.alert("{}".format(error), level=0)
        
              
class SSL_Client(mpre.network.Tcp_Client):
        
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
    
    defaults = mpre.network.Tcp_Socket.defaults.copy()
    defaults.update(SSL_DEFAULTS)
    defaults.update({"server_side" : True,
                     "certfile" : "server.crt",
                     "keyfile" : "server.key"})
    
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
        self.alert("Authenticated", level=0)
                
        
class SSL_Server(mpre.network.Server):
    
    defaults = mpre.network.Server.defaults.copy()
    defaults.update(SSL_DEFAULTS)
    defaults.update({"port" : 443,
                     "Tcp_Socket_type" : "mpre.networkssl.SSL_Socket"})       