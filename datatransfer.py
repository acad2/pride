""" pride.datatransfer - Authenticated services for transferring data on a network
    Constructs a service for the transfer of arbitrary data from one registered 
    party to another. """
    
import pride.authentication2

class Data_Transfer_Client(pride.authentication2.Authenticated_Client):
    """ Client program for sending data securely to a party registered
        with the target service. """
    defaults = {"target_service" : "->Python->Data_Transfer_Service"}
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
            
            
class Data_Transfer_Service(pride.authentication2.Authenticated_Service):
    """ Service for transferring arbitrary data from one registered client to another """        
    mutable_defaults = {"messages" : dict}
    remotely_available_procedures = ("send_to", )
    verbosity = {"refresh" : 'v', "data_transfer" : 0}
    
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
        
        
def test_dts():
    objects["->Python"].create(Data_Transfer_Service)
    client1 = Data_Transfer_Client(username="Ella")
    client2 = Data_Transfer_Client(username="Not_Ella")
    return client1, client2
    