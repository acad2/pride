""" pride.datatransfer - Authenticated services for transferring data on a network
    Constructs a service for the transfer of arbitrary data from one registered 
    party to another. """
    
import pride.authentication2
import pride.shell
import pride.utilities

def file_operation(filename, mode, method, file_type="open", offset=None, data=None):
    with invoke(file_type, filename, mode) as _file:
        if offset is not None:
            _file.seek(offset)
        if method == "write":
            assert data is not None
            print data
            _file.write(data)
            _file.flush()
        else:
            assert method == "read"
            return _file.read(data)            
            
class Data_Transfer_Client(pride.authentication2.Authenticated_Client):
    """ Client program for sending data securely to a party registered
        with the target service. """
    defaults = {"target_service" : "/Python/Data_Transfer_Service"}
    verbosity = {"send_to" : "vv"}
    
    @pride.authentication2.remote_procedure_call(callback_name="receive")
    def send_to(self, receiver, message): 
        """ Sends message to receiver via remote procedure call through 
            self.target_service@self.ip. Automatically returns any messages
            sent to self from other clients.
            
            Passing an empty string for the receiver argument will return any
            messages that have been sent to self. """
        
    def receive(self, messages):
        """ Receives messages and supplies them to alert for user notification.
            self.verbosity may feature usernames of other clients; entries not
            found default to 0. """
        for sender, message in messages:
            self.alert("{}: {}", (sender, message), level=self.verbosity.get(sender, 0))
            
    def refresh(self):
        """ Checks for new data from the server """
        self.send_to('', '')
        
        
class Data_Transfer_Service(pride.authentication2.Authenticated_Service):
    """ Service for transferring arbitrary data from one registered client to another """        
    mutable_defaults = {"messages" : dict}
    remotely_available_procedures = ("send_to", )
    verbosity = {"refresh" : 'v', "data_transfer" : 'v'}
    
    def send_to(self, receiver, message):        
        sender = self.session_id[self.current_session[0]]
        if receiver:
            self.alert("{} Sending {} bytes to {}", 
                       (sender, len(message), receiver),
                       level=self.verbosity["data_transfer"])
            try:
                self.messages[receiver].append((sender, message))
            except KeyError:
                self.messages[receiver] = [(sender, message)]
        else:
            self.alert("Sending messages back to: {}", (sender, ), 
                       level=self.verbosity["refresh"])
        return self.messages.pop(sender, tuple())
        
    
class File_Transfer(Data_Transfer_Client):
    
    defaults = {"filename" : '', "file" : None, "receivers" : tuple(),
                "file_type" : "open", 
                "permission_string" : ("{}:{} Accept file transfer from '{}'?" + 
                                       "\n'{}' ({} bytes) ")}
        
    def __init__(self, **kwargs):
        super(File_Transfer, self).__init__(**kwargs)        
        if self.file or self.filename:
            _file = self.file or open(self.filename, "a+b")
            data = _file.read()
            if len(data) < 65535:                
                packet = pride.utilities.save_data(self.filename, 0, data)
                ip = self.ip
                port = self.port
                for receiver in self.receivers:
                    self.alert("Sending packet to: {}@{}:{}",
                               (receiver, ip, port), level=0)
                    self.send_to(receiver, packet)
            else:
                raise NotImplementedError()
        else: # this must be a download            
            self.refresh()
            
    def receive(self, messages):
        for sender, message in messages:
            filename, offset, data = pride.utilities.load_data(message)
            if pride.shell.get_permission(self.permission_string.format(self.username, self.reference, 
                                                                        sender, filename, len(data))):
                filename = raw_input("Please enter the filename or press enter to use '{}': ".format(filename)) or filename
                file_operation(filename, "a+b", "write", self.file_type, offset, data)
                            

class File_Storage_Daemon(Data_Transfer_Client):
    
    defaults = {"username" : "File_Storage_Daemon", "file_type" : ''}
    verbosity = {"invalid_request_type" : 0}
    
    def receive(self, message):
        for sender, message in message:
            request_type, packet = pride.utilities.load_data(message)
            filename, offset, data = pride.utilities.load_data(packet)             
            if request_type == "save":
                file_operation(filename, "a+b", "write", self.file_type, offset, data)
                try:
                    self.file_access[sender].add(filename)
                except KeyError:
                    self.file_access[sender] = set((filename, ))
                    
            elif request_type == "load":
                if filename in self.file_access[sender]:
                    self.send_to(sender, file_operation(filename, "rb", "read", self.file_type, offset, data))
            else:
                self.alert("Received unsupported request_type '{}' from '{}'\npacket: {}",
                           (request_type, sender, packet), level=self.verbosity["invalid_request_type"])
            
    
class Proxy(Data_Transfer_Client):
    
    defaults = {"username" : "Proxy", "auto_register" : True}
    
    def receive(self, messages):
        for sender, message in messages:
            target, packet = pride.utilities.load_data(message)            
            self.send_to(target, packet)
            
            
def test_dts():
    client1 = Data_Transfer_Client(username="Ella")
    client2 = Data_Transfer_Client(username="Not_Ella")
    return client1, client2
    
def test_File_Transfer():
    file_transfer1 = File_Transfer(username="Ella")                                        
    file_transfer2 = File_Transfer(filename="base_Copy.py", username="Not_Ella",
                                   receivers=("Not_Ella", "Ella"))
    
if __name__ == "__main__":
    test_File_Transfer()