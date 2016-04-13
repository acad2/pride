import pride.authentication2

class Black_Box_Service(pride.authentication2.Authenticated_Service):
    
    defaults = {"input_types" : ("keyboard", "mouse")}
    remotely_available_procedures = ("handle_input", )
    verbosity = {"handle_keyboard" : 0, "handle_mouse" : 0}
    
    def handle_input(self, packed_user_input):
        input_type, input_values = packed_user_input.split(' ', 1)
        if input_type in self.input_types:
            getattr(self, "handle_" + input_type)(input_values)
            
    def handle_keyboard(self, input_bytes):
        self.alert("Received keystrokes: {}".format(input_bytes), 
                   level=self.verbosity["handle_keyboard"])
                   
    def handle_mouse(self, mouse_info):
        self.alert("Received mouse info: {}".format(mouse_info),
                   level=self.verbosity["handle_mouse"])
                   
                   
class Black_Box_Client(pride.authentication2.Authenticated_Client):
                    
    defaults = {"target_service" : "->Python->Black_Box_Service"}
    verbosity = {"handle_input" : 0, "receive_response" : 0}
    
    def __init__(self, **kwargs):
        super(Black_Box_Client, self).__init__(**kwargs)
        pride.objects["->User->Command_Line"].set_default_program(self.reference, (self.reference, "handle_keyboard"))                 
        
    @pride.authentication2.remote_procedure_call(callback_name="receive_response")
    def handle_input(self, packed_user_input): 
        pass
        
    def handle_keyboard(self, input_bytes):
        self.handle_input("keyboard " + input_bytes)
        
    def handle_mouse(self, mouse_info):
        self.handle_input("mouse " + input_bytes)
    
    def receive_response(self, data):
        self.alert("Received response: {}".format(data), 
                   level=self.verbosity["receive_response"])
                   
def test_black_box_service():
    try:
        pride.objects["->User->Command_Line"]
    except KeyError:
        pride.objects["->User"].create("pride.shell.Command_Line")
    service = pride.objects["->Python"].create(Black_Box_Service)
    client = Black_Box_Client(username="localhost")    
    
if __name__ == "__main__":
    test_black_box_service()
    