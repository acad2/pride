import pride.authentication2

class Data_Transfer_Client(pride.authentication2.Authenticated_Client):
    
    defaults = {"target_service" : "->Python->Data_Transfer_Service"}
    verbosity = {"send_to" : "vv"}
    
    @pride.authentication2.remote_procedure_call(callback_name="receive")
    def send_to(self, receiver, message): pass
        
    def receive(self, messages):
        for sender, message in messages:
            self.alert("{}: {}", (sender, message), level=self.verbosity.get(sender, 0))
            
            
class Data_Transfer_Service(pride.authentication2.Authenticated_Service):
            
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
        
        
class Voip_Client(Data_Transfer_Client):
   
    defaults = {"audio_input_name" : "->Python->Audio_Manager->Audio_Input",
                "audio_output_name" : "->Python->Audio_Manager->Audio_Output",
                "receivers" : tuple()}
    required_attributes = ("receivers", )  
    
    def __init__(self, **kwargs):
        super(Voip_Client, self).__init__(**kwargs)
        pride.objects[self.audio_input_name].add_listener(self.reference)
     
    def handle_audio_input(self, audio_data):
        for receiver in self.receivers:
            self.send_to(receiver, audio_data)
            
    def receive(self, messages):
        for sender, message in messages:
            self.alert("Got {} bytes of audio data from {}",
                       (len(message), sender), level=0)
        
def test_dts():
    objects["->Python"].create(Data_Transfer_Service)
    client1 = Data_Transfer_Client(username="Ella")
    client2 = Data_Transfer_Client(username="Not_Ella")
    return client1, client2
    