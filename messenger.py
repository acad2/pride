import pride.datatransfer
import pride.audio

class Messenger(pride.datatransfer.Data_Transfer_Client):
    
    defaults = {"audio_input_device" : "/Python/Audio_Manager/Audio_Input",
                "audio_output_device" : "/Python/Audio_Manager/Audio_Output"}
                
    mutable_defaults = {"send_audio_to" : list}
     
    verbosity = {"failed_to_enable_microphone" : 0, "failed_to_disable_microphone" : 0,
                 "receive_text" : 0}
    
    def receive(self, messages):
        for sender, packet in messages:
            if packet[:5] == "audio":
                self.handle_incoming_audio(data)
            else:                
                self.handle_text(sender, packet)
                
    def handle_incoming_audio(self, data):
        self.alert("Received audio data", level=0)
        pride.objects[self.audio_output_device].handle_audio_input(data)
        
    def enable_microphone(self):
        try:
            pride.objects[self.audio_input_device].add_listener(self.reference)
        except KeyError:
            try:
                pride.audio.enable()
            except ValueError:
                self.alert("Failed to enable microphone", level=self.verbosity["failed_to_enable_microphone"])
            else:
                pride.objects[self.audio_input_device].add_listener(self.reference)
                
    def disable_microphone(self):
        try:
            pride.objects[self.audio_input_device].remove_listener(self.reference)
        except KeyError:
            self.alert("Failed to disable microphone", level=self.verbosity["failed_to_disable_microphone"])
        
    def handle_audio_input(self, audio_data):
        for receiver in self.send_audio_to:
            self.send_to(receiver, "audio " + audio_data)
            
    def handle_text(self, sender, packet):
        self.alert("{}: {}".format(sender, packet), 
                   level=self.verbosity.get("{}_text".format(sender), self.verbosity["receive_text"]))
                   