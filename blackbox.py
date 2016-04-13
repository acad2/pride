import pride.authentication2
import pride.utilities

class Event_Structure(object):
    
    def __init__(self, mouse):
        self.button = mouse
        
        
class Mouse_Structure(object):
            
    def __init__(self, x, y, clicks, button):
        self.x = x
        self.y = y
        self.clicks = clicks
        self.button = button
        
    def __str__(self):
        return "Mouse(x={}, y={}, clicks={}, button={})".format(self.x, self.y, self.clicks, self.button)
        
    
class Black_Box_Service(pride.authentication2.Authenticated_Service):
    
    defaults = {"input_types" : ("keyboard", "mouse"), "window_type" : "pride.gui.blackbox.Service_Window"}
    remotely_available_procedures = ("handle_input", )
    verbosity = {"handle_keyboard" : 0, "handle_mouse" : 0}
    mutable_defaults = {"windows" : dict}
    
    def on_login(self):
        username = self.current_user
        self.windows[username] = pride.objects["->Python->SDL_Window"].create(self.window_type)
        
    def handle_input(self, packed_user_input):
        input_type, input_values = packed_user_input.split(' ', 1)
        if input_type in self.input_types:
            getattr(self, "handle_" + input_type)(input_values)
            
    def handle_keyboard(self, input_bytes):
        self.alert("Received keystrokes: {}".format(input_bytes), 
                   level=self.verbosity["handle_keyboard"])
                   
    def handle_mouse(self, mouse_info):
        mouse = Mouse_Structure(*pride.utilities.load_data(mouse_info))
        pride.objects["->Python->SDL_Window->SDL_User_Input"].handle_mousebuttondown(Event_Structure(mouse))
        self.alert("Received mouse info: {}".format(mouse),
                   level=self.verbosity["handle_mouse"])
                   
                   
class Black_Box_Client(pride.authentication2.Authenticated_Client):
                    
    defaults = {"target_service" : "->Python->Black_Box_Service", "mouse_support" : True}
    verbosity = {"handle_input" : 0, "receive_response" : 0}
    
    def __init__(self, **kwargs):
        super(Black_Box_Client, self).__init__(**kwargs)
        pride.objects["->User->Command_Line"].set_default_program(self.reference, (self.reference, "handle_keyboard"))                 
        if self.mouse_support:
            pride.objects["->Python->SDL_Window"].create("pride.gui.blackbox.Client_Window", client=self.reference)
            
    @pride.authentication2.remote_procedure_call(callback_name="receive_response")
    def handle_input(self, packed_user_input): 
        pass
        
    def handle_keyboard(self, input_bytes):
        self.handle_input("keyboard " + input_bytes)
        
    def handle_mouse(self, mouse_info):        
        self.handle_input("mouse " + mouse_info)
    
    def receive_response(self, data):
        self.alert("Received response: {}".format(data), 
                   level=self.verbosity["receive_response"])
                   
                                      
def test_black_box_service():
    import pride
    import pride.gui
    try:
        pride.objects["->User->Command_Line"]
    except KeyError:
        pride.objects["->User"].create("pride.shell.Command_Line")
    import pride.gui
    pride.gui.enable()
    service = pride.objects["->Python"].create(Black_Box_Service)
    client = Black_Box_Client(username="localhost")    
    
if __name__ == "__main__":
    test_black_box_service()
    