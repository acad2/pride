""" Provides network services that do not reveal information about how 
    application logic produces its result. Black_Box_Services receive input
    in the form of keystrokes, mouse clicks, and potentially audio,
    operate on the input in a manner opaque to the client, and return output
    to the client. """
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

    defaults = {"input_types" : ("keyboard", "mouse", "audio"), "window_type" : "pride.gui.sdllibrary.Window_Context"}
    remotely_available_procedures = ("handle_input", )
    verbosity = {"handle_keyboard" : 0, "handle_mouse" : 'v', "handle_audio" : 0, "refresh" : 'v'}
    mutable_defaults = {"windows" : dict}
    
    def on_login(self):
        username = self.current_user
        window =  self.create(self.window_type)
        self.windows[username] = window.reference
        window.create("pride.gui.widgetlibrary.Homescreen")
        
    def handle_input(self, packed_user_input):
        input_type, input_values = packed_user_input.split(' ', 1)
        if input_type in self.input_types:
            return getattr(self, "handle_{}_input".format(input_type))(input_values)
        else:            
            raise ValueError("Unaccepted input_type: {}".format(packed_user_input))
            
    def handle_keyboard_input(self, input_bytes):
        self.alert("Received keystrokes: {}".format(input_bytes), 
                   level=self.verbosity["handle_keyboard"])
                      
    def handle_mouse_input(self, mouse_info): 
        user_window = pride.objects[self.windows[self.current_user]]
        if mouse_info:            
            mouse = Mouse_Structure(*pride.utilities.load_data(mouse_info))
            self.alert("Received mouse info: {}".format(mouse), level=self.verbosity["handle_mouse"])
            user_window.user_input.handle_mousebuttondown(Event_Structure(mouse))
        else:
            self.alert("Received window refresh request", level=self.verbosity["refresh"])                   
        
        instructions = user_window.run()    
        return "draw", instructions
        
    def handle_audio_input(self, audio_bytes):
        self.alert("Received audio: {}...".format(audio_bytes[:50]), 
                   level=self.verbosity["handle_audio"])
        
        
class Black_Box_Client(pride.authentication2.Authenticated_Client):
                    
    defaults = {"target_service" : "->Python->Black_Box_Service", 
                "mouse_support" : False, "refresh_interval" : .95,
                "audio_support" : False, "audio_source" : "->Python->Audio_Manager->Audio_Input",
                "microphone_on" : False,
                "response_methods" : ("handle_response_draw", )}
                
    verbosity = {"handle_input" : 'v', "receive_response" : 'v', "receive_null_response" : 'v'}
    flags = {"_refresh_flag" : False}
        
    def __init__(self, **kwargs):
        super(Black_Box_Client, self).__init__(**kwargs)
        pride.objects["->User->Command_Line"].set_default_program(self.reference, (self.reference, "handle_keyboard_input"))                 
        if self.mouse_support:
            pride.objects[self.sdl_window].create("pride.gui.blackbox.Client_Window", client=self.reference)
            self.refresh_instruction = pride.Instruction(self.reference, "_refresh")
            self.refresh_instruction.execute(priority=self.refresh_interval)
        if self.audio_support:
            pride.objects[self.audio_source].add_listener(self.reference)
            
    @pride.authentication2.remote_procedure_call(callback_name="receive_response")
    def handle_input(self, packed_user_input): 
        pass
        
    def handle_keyboard_input(self, input_bytes):
        self.handle_input("keyboard " + input_bytes)
        
    def handle_mouse_input(self, mouse_info):  
        self._refresh_flag = False
        self.handle_input("mouse " + mouse_info)
    
    def handle_audio_input(self, audio_bytes):
        if self.microphone_on:
            self.handle_input("audio " + audio_bytes)
        
    def receive_response(self, packet):
        try:
            _type, data = packet
        except TypeError:            
            self.alert("Received null response", level=self.verbosity["receive_null_response"])
            assert packet is None
        else:
            self.alert("Received response: {}".format(_type), level=self.verbosity["receive_response"])
            response_method = "handle_response_{}".format(_type)        
            if response_method in self.response_methods:
                getattr(self, response_method)(data)
            else:
                self.alert("Unsupported response method: '{}'".format(response_method), level=0)
            
    def handle_response_draw(self, draw_instructions):         
        if draw_instructions:
            pride.objects[self.sdl_window].draw(draw_instructions)        
    
    def _refresh(self):
        if self._refresh_flag:                    
            self.handle_mouse_input('')
        self.refresh_instruction.execute(priority=self.refresh_interval)
        self._refresh_flag = True
        
def test_black_box_service():
    import pride
    import pride.gui
    import pride.audio
    try:
        pride.objects["->User->Command_Line"]
    except KeyError:
        pride.objects["->User"].create("pride.shell.Command_Line")    
    window = pride.gui.enable()
    pride.audio.enable()
    service = pride.objects["->Python"].create(Black_Box_Service)
    client = Black_Box_Client(username="localhost", sdl_window=window, mouse_support=True, audio_support=True)    
    
if __name__ == "__main__":
    test_black_box_service()
    