import pride.authentication2

class Messenger_Client(pride.authentication2.Authenticated_Client):
    
    defaults = {"target_service" : "->Python->Messenger_Service"}
    verbosity = {"send_message" : "vv"}
    
    @pride.authentication2.remote_procedure_call(callback_name="receive_messages")
    def send_message(self, receiver, message): pass
        
    def receive_messages(self, messages):
        for sender, message in messages:
            self.alert("{}: {}", (sender, message), level=self.verbosity.get(sender, 0))
            
            
class Messenger_Service(pride.authentication2.Authenticated_Service):
            
    mutable_defaults = {"messages" : dict}
    remotely_available_procedures = ("send_message", )
    def send_message(self, receiver, message):
        sender = self.session_id[self.current_session[0]]
        if receiver:
            try:
                self.messages[receiver].append((sender, message))
            except KeyError:
                self.messages[receiver] = [(sender, message)]
        else:
            self.alert("Sending messages back to: {}", (sender, ), level=0)
        return self.messages.pop(sender, tuple())
        
def test_messenger():
    objects["->Python"].create(Messenger_Service)
    client1 = Messenger_Client(username="Ella")
    client2 = Messenger_Client(username="Not_Ella")
    return client1, client2
    #client1.send_message("Not_Ella", "Hey what's up!")
    #client2.send_message("Ella", "Just programming away ^.^")
    #import pride
    #pride.Instruction(client1.reference, "send_message", '', '').execute(priority=1)
    