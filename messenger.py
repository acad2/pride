import pride.datatransfer
import pride.audio

class Messenger(pride.datatransfer.Data_Transfer_Client):
    
    defaults = {"audio_input_device" : "/Python/Audio_Manager/Audio_Input",
                "audio_output_device" : "/Python/Audio_Manager/Audio_Output"}
                
    mutable_defaults = {"send_audio_to" : list}
     
    verbosity = {"failed_to_enable_microphone" : 0, "failed_to_disable_microphone" : 0}
    
    def receive(self, messages):
        for sender, packet in messages:
            request_type, data = packet.split(' ', 1)
            if request_type == "audio":
                self.handle_incoming_audio(data)
            else:
                assert request_type == "text"
                self.handle_text(data)
                
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
            