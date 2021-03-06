import sys
import os
import ssl

import pride.base
import pride.network
import pride.utilities
import pride.shell

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
                "dont_save" : True,
                "server_hostname" : None,
                "check_hostname" : False}
                
try:
    raise AttributeError
    TEST_CONTEXT = ssl.create_default_context()
except AttributeError: # old ssl; will use ssl.wrap_socket
    WRAP_SOCKET_OPTIONS = ("keyfile", "certfile", "server_side", "cert_reqs", 
                           "ssl_version", "ca_certs", "do_handshake_on_connect", 
                           "suppress_ragged_eofs", "ciphers")      
else: # python 2.7.9+ will use SSLContext.wrap_socket
    WRAP_SOCKET_OPTIONS = ("server_side", "do_handshake_on_connect", 
                           "suppress_ragged_eofs", "server_hostname")

        
def generate_self_signed_certificate(name=""): # to do: pass in ssl commands and arguments
    """ Creates a name.key, name.csr, and name.crt file. These files can
        be used for the keyfile and certfile options for an ssl server socket"""
    name = name or raw_input("Please provide the name for the .key, .crt, and .csr files: ", must_reply=True)
    OPENSSL = r"C:\\OpenSSL-Win32\\bin\\openssl.exe"# {} genrsa -aes256 -passout pass:x -out {}.pass.key 2048"
    OPENSSL64 = r"C:\\OpenSSL_Win64\\bin\openssl.exe"
    if os.path.exists(OPENSSL):
        openssl = OPENSSL 
    elif os.path.exists(OPENSSL64):
        openssl = OPENSSL64
    else:
        openssl = "openssl"
        
    shell = pride.utilities.shell        
    shell("{} genrsa -aes256 -passout pass:x -out {}.pass.key 2048".format(openssl, name), True)
    shell("{} rsa -passin pass:x -in {}.pass.key -out {}.key".format(openssl, name, name), True)
    shell("{} req -new -key {}.key -out {}.csr".format(openssl, name, name), True)
    shell("{} x509 -req -days 365 -in {}.csr -signkey {}.key -out {}.crt".format(openssl, name, name, name), True)
    os.remove("{}.pass.key".format(name))    
               
def generate_rsa_keypair(name=''):
    shell = pride.utilities.shell
    shell("openssl genrsa -out {}_private_key.pem 4096".format(name))
    shell("openssl rsa -pubout -in {}_private_key.pem -out {}_public_key.pem".format(
          name))
            
class SSL_Client(pride.network.Tcp_Client):
    
    """ An asynchronous client side Tcp socket wrapped in an ssl socket.
        Users should extend on_ssl_authentication instead of on_connect to
        initiate data transfer; on_connect is used to start the
        ssl handshake"""
    defaults = SSL_DEFAULTS

    def on_connect(self):
        super(SSL_Client, self).on_connect()
        try:
            raise AttributeError
            context = ssl.create_default_context()            
        except AttributeError:
            wrap_socket = ssl.wrap_socket
        else:
            context.load_verify_location
            wrap_socket = context.wrap_socket  
            if not self.check_hostname:
                context.check_hostname = False
            else:
                assert context.check_hostname
                assert self.server_hostname
        self.ssl_socket = wrap_socket(self.socket, 
                                      **dict((attribute, 
                                              getattr(self, attribute)) for
                                              attribute in 
                                              WRAP_SOCKET_OPTIONS))
        self.ssl_connect()        
        
    def ssl_connect(self):
        try:
            self.ssl_socket.do_handshake()
        except ssl.SSLError as error:
            if error.errno != ssl.SSL_ERROR_WANT_READ:
                self.alert("Unhandled SSLError when performing handshake: {}",
                           [error], level=0)
                raise
        else:
            self.ssl_authenticated = True
            self.on_ssl_authentication()    
            
    def on_select(self):
        if self.connected and not self.ssl_authenticated:
            self.ssl_connect()
        else:
            super(SSL_Client, self).on_select()
                        
    def on_ssl_authentication(self):
        self.alert("Authenticated", level=0)
            
        
class SSL_Socket(pride.network.Tcp_Socket):    
    """ An asynchronous server side client socket wrapped in an ssl socket.
        Users should override the on_ssl_authentication method instead of
        on_connect. """
        
    defaults = {"ssl_authenticated" : False}
     
    def on_connect(self):
        super(SSL_Socket, self).on_connect()
        parent = self.parent
        self.ssl_socket = parent.wrap_socket(self, **dict((attribute, 
                                                           getattr(parent, 
                                                                   attribute)) 
                                                           for attribute in WRAP_SOCKET_OPTIONS))
        
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
                self.alert("Unhandled SSLError when performing handshake: {}",
                           [error], level=0)  
                raise
        else:
            self.ssl_authenticated = True
            self.on_ssl_authentication()
            
    def on_ssl_authentication(self):
        self.alert("Authenticated", level='v')
                
        
class SSL_Server(pride.network.Server):
    
    defaults = SSL_DEFAULTS
    defaults.update({"port" : 443, "Tcp_Socket_type" : "pride.networkssl.SSL_Socket",
                     "dont_save" : False, "server_side" : True,                     
                     # configurable
                     "certfile" : '', "keyfile" : '', #.crt and .key
                     "update_site_config_on_new_certfile" : True})       
        
    verbosity = {"certfile_not_found" : 0, "certfile_generated" : 0}
    
    def __init__(self, **kwargs):
        super(SSL_Server, self).__init__(**kwargs)
        
        # some stuff to streamline the first run/install process
        if not os.path.exists(self.certfile) or not os.path.exists(self.keyfile):
            if self.certfile or self.keyfile:
                self.alert("Certificate/Key file not found: '{}''{}'\n", (self.certfile, self.keyfile),
                           level=self.verbosity["certfile_not_found"])
            else:
                self.alert("Usage of ssl requires certificates and key files.", level=0)
            if pride.shell.get_permission("{}: Generate a new self signed certificate and key now?: ".format(self.reference)):
                filename = raw_input("(Optional) Please provide the filepaths for the .key, .crt, and .csr files: ")  
                if not filename:
                    filename = "ssl_server"
                if not os.path.split(filename)[0]: # no directory supplied or no filename
                    filename = os.path.join(pride.site_config.PRIDE_DIRECTORY, filename)
                                        
                self.create("pride.programs.create_self_signed_certificate.Self_Signed_Certificate", name=filename)
                self.alert("Self signed certificate generated; Continuing.", 
                           level=self.verbosity["certfile_generated"])
                self.certfile = filename + ".crt"
                self.keyfile = filename + ".key"
                
                if (self.update_site_config_on_new_certfile and
                    not hasattr(pride.site_config, "pride_rpc_Rpc_Server_defaults")):
                    
                    pride.site_config.write_to("pride_rpc_Rpc_Server_defaults", 
                                               certfile=r"{}.crt".format(filename),
                                               keyfile=r"{}.key".format(filename))       
            else:
                raise ValueError("pride.network.SSL_Server requires a certificate and key;" +
                                 " Unable to load certificate file; Unable to continue")            
        try:
            raise AttributeError
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        except AttributeError:
            wrap_socket = ssl.wrap_socket
        else:
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
            wrap_socket = context.wrap_socket   
        self.wrap_socket = wrap_socket
        
    def __getstate__(self):
        attributes = super(SSL_Server, self).__getstate__()
        del attributes["wrap_socket"]
        return attributes
        
    def on_load(self, state):
        super(SSL_Server, self).on_load(state)
        self.wrap_socket = ssl.wrap_socket # hardcoded for now
        