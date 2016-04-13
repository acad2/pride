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
    
    defaults = {"input_types" : ("keyboard", "mouse", "audio"), "window_type" : "pride.gui.blackbox.Service_Window"}
    remotely_available_procedures = ("handle_input", )
    verbosity = {"handle_keyboard" : 0, "handle_mouse" : 0, "handle_audio" : 0}
    mutable_defaults = {"windows" : dict}
    
    def on_login(self):
        username = self.current_user
        self.windows[username] = pride.objects["->Python->SDL_Window"].create(self.window_type)
        
    def handle_input(self, packed_user_input):
        input_type, input_values = packed_user_input.split(' ', 1)
        if input_type in self.input_types:
            getattr(self, "handle_{}_input".format(input_type))(input_values)
        else:            
            raise ValueError("Unaccepted input_type: {}".format(packed_user_input))
            
    def handle_keyboard_input(self, input_bytes):
        self.alert("Received keystrokes: {}".format(input_bytes), 
                   level=self.verbosity["handle_keyboard"])
                      
    def handle_mouse_input(self, mouse_info):
        mouse = Mouse_Structure(*pride.utilities.load_data(mouse_info))
        pride.objects["->Python->SDL_Window->SDL_User_Input"].handle_mousebuttondown(Event_Structure(mouse))
        self.alert("Received mouse info: {}".format(mouse),
                   level=self.verbosity["handle_mouse"])
                   
    def handle_audio_input(self, audio_bytes):
        self.alert("Received audio: {}...".format(audio_bytes[:50]), 
                   level=self.verbosity["handle_audio"])
    
    
class Black_Box_Client(pride.authentication2.Authenticated_Client):
                    
    defaults = {"target_service" : "->Python->Black_Box_Service", 
                "mouse_support" : True,
                "audio_support" : True, "audio_source" : "->Python->Audio_Manager->Audio_Input",
                "microphone_on" : False}
    verbosity = {"handle_input" : 0, "receive_response" : 0}
    
    def __init__(self, **kwargs):
        super(Black_Box_Client, self).__init__(**kwargs)
        pride.objects["->User->Command_Line"].set_default_program(self.reference, (self.reference, "handle_keyboard_input"))                 
        if self.mouse_support:
            pride.objects["->Python->SDL_Window"].create("pride.gui.blackbox.Client_Window", client=self.reference)
        if self.audio_support:
            pride.objects[self.audio_source].add_listener(self.reference)
            
    @pride.authentication2.remote_procedure_call(callback_name="receive_response")
    def handle_input(self, packed_user_input): 
        pass
        
    def handle_keyboard_input(self, input_bytes):
        self.handle_input("keyboard " + input_bytes)
        
    def handle_mouse_input(self, mouse_info):        
        self.handle_input("mouse " + mouse_info)
    
    def handle_audio_input(self, audio_bytes):
        if self.microphone_on:
            self.handle_input("audio " + audio_bytes)
        
    def receive_response(self, data):
        self.alert("Received response: {}".format(data), 
                   level=self.verbosity["receive_response"])
                   
                                      
def test_black_box_service():
    import pride
    import pride.gui
    import pride.audio
    try:
        pride.objects["->User->Command_Line"]
    except KeyError:
        pride.objects["->User"].create("pride.shell.Command_Line")    
    pride.gui.enable()
    pride.audio.enable()
    service = pride.objects["->Python"].create(Black_Box_Service)
    client = Black_Box_Client(username="localhost")    
    
if __name__ == "__main__":
    test_black_box_service()
    