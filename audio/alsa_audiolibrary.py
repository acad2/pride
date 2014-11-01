import alsaaudio
import array
import pickle
import struct
import wave
import time
from contextlib import contextmanager
from sys import platform, exit
from ctypes import CFUNCTYPE, c_int, c_char_p, cdll

import base
import defaults
Event = base.Event


class Wav_File(base.Base):
    
    defaults = defaults.Wav_File
    
    def __init__(self, **kwargs):
        super(Wav_File, self).__init__(**kwargs)
        self.file = wave.open(self.filename, self.mode)
        channels, sample_width, rate, number_of_frames, comptype, compname = self.file.getparams()
        self.channels = channels
        self.sample_width = sample_width
        self.rate = rate
        self.number_of_frames = number_of_frames
        self.comptype = comptype
        self.compname = compname
        #v: print "opened wav file with", channels, format, rate, number_of_frames
        
    def read(self, size):
        data = self.file.readframes(size)
        if self.repeat and (self.file.tell() == self.number_of_frames):
            self.file.rewind()
        return data
        
    def tell(self):
        return self.file.tell()
        
    def write(self, data):
        self.file.writeframes(data)
        
    def close(self):
        self.file.close()
        
        
class Audio_Device(base.Base):
    
    possible_options = ("rate", "channels", "format", "sample_size", "period", "type", "card")
    def _get_options(self):
        options = {}
        for option in self.possible_options:
            value = getattr(self, option, None)
            if value:
                options[option] = value
        return options
    options = property(_get_options)
    defaults = defaults.AlsaAudio_Device
    
    def __init__(self, **kwargs):
        super(Audio_Device, self).__init__(**kwargs)            
        self.name = self.card
        
    def initialize(self):
        self.pcm = alsaaudio.PCM(type=self.type, mode=self.mode, card=self.card)
        self.pcm.setnchannels(self.channels)
        self.pcm.setrate(self.rate)
        self.pcm.setformat(self.format)
        self.sample_size = self.sample_size
        self.pcm.setperiod(self.period)
        self.thread = self._new_thread()
        if self.recording:
            self.file = self._new_wave_file()
    
    def _new_thread(self):
        raise NotImplementedError
        
    def _new_wave_file(self):
        """create a new wave file of appropriate format"""
        filename = ("%s recording.wav" % self.name).replace(" ", "_")
        try:
            file = wave.open(filename, "wb")
        except IOError:
            print "unusable default filename %s" % (self.name)
            file = wave.open("%s.wav" % raw_input("Please enter filename: "), "wb")
        file.setnchannels(self.channels)
        file.setsampwidth(self.sample_size)
        file.setframerate(self.rate)
        print "created wave file: channels %s, sample width %s, rate %s" % (self.channels, PORTAUDIO.get_sample_size(self.format), self.rate)
        return file
         
         
class Audio_Input(Audio_Device):
    
    defaults = defaults.AlsaAudio_Input
    
    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)
        
    def _new_thread(self):
        while True:
            self.data = self.pcm.read()
            yield
            
    def next_frame(self):
        next(self.thread)
        

class Audio_Output(Audio_Device):
                
    defaults = defaults.AlsaAudio_Output
    
    def __init__(self, **kwargs):
        super(Audio_Output, self).__init__(**kwargs)
        
    def _new_thread(self):
        while True:
            self.pcm.write(self.data_source.read(self.period_size))
            yield
            
    def next_frame(self):
        next(self.thread)
        
        
class Alsa_Audio_Configuration_Utility(base.Process):
        
    defaults = defaults.Audio_Configuration_Utility
    
    def __init__(self, **kwargs):
        self.selected_devices = []
        super(Audio_Configuration_Utility, self).__init__(**kwargs)
        
        if "default" in self.mode:
            default_input, default_output = self.get_default_devices()
            self.selected_devices.append(default_input)
            self.selected_devices.append(default_output)
            self.write_config_file(self.selected_devices)
            self.delete()
        else:
            self.all_devices = self.get_all_devices()
            Event("Audio_Configuration_Utility", "run", component=self).post()
    
    def write_config_file(self, device_list):
        with open(self.config_file_name, "wb") as config_file:
            for device in device_list:
                print device
            pickle.dump(device_list, config_file)
            config_file.flush()
            config_file.close()
            
    def get_all_devices(self):
        return dict((index, device_name) for index, device_name in enumerate(alsaaudio.cards()))

    def print_display_devices(self, device_dict):
        for key, value in device_dict.items():
            print "%s: %s" % (key, value)
        
    def get_selections(self):
        selection = ""
        self.selected_devices = []
    
        while "done" not in selection:
            print "\n"*80
            print "type 'done' to finish selecting..."
            print "**************************************"
            self.print_display_devices(self.all_devices)
            print "currently using: ", [str(item) for item in self.selected_devices]
            selection = raw_input("Enter index of input device to use: ")
            try:
                index = int(selection)
            except ValueError:
                if selection == "done":
                    break
                else:
                    raw_input("Invalid index. Press enter to continue...")
            else:
                try:
                    device = self.all_devices[index]
                except KeyError:
                    selection = raw_input("Invalid index. press enter to continue to or 'done' to finish")
                    if 'done' in selection:
                        break
                else:              
                    self.selected_devices.append(device)
        print "finished selecting devices"        
    
    @staticmethod
    def get_default_devices():
        raise NotImplementedError     
    
    def run(self):
        self.get_selections()
        self.write_config_file(self.selected_devices)
        self.delete()
        if getattr(self, "exit_when_finished", None):
            exit()

        
class Audio_Manager(base.Process):
    
    defaults = defaults.Audio_Manager
    
    def _get_devices(self):
        return self.objects.get("Audio_Input", []) + self.objects.get("Audio_Output", [])
        
    audio_devices = property(_get_devices)
    
    def __init__(self, **kwargs):
        self.listeners = {}
        super(Audio_Manager, self).__init__(**kwargs)
        if self.config_file_name:
            try:
                self.load_config_file()       
            except:
                raise
                raw_input("Please run audio_config_utility. No config file found")
                Event("System0", "exit").post()
        elif self.use_defaults:
            raise NotImplementedError
            input_info, output_info = Audio_Configuration_Utility.get_default_devices()
            input = self.create(Audio_Input, input_info)
            output = self.create(Audio_Output, output_info)
            input.initialize()
            output.initialize()
            self.listeners[input.name] = []
            self.listeners[output.name] = []
    
    def load_config_file(self):
        with open(self.config_file_name, "rb") as config_file:
            for device_name in pickle.load(config_file):
                device = self.create(Audio_Input, card=device_name)
                self.listeners[device.name] = []
                device.initialize()

    def send_channel_info(self, listener):
        """usage: Event("Audio_Manager0", "send_channel_info", my_object).post() 
        => Message: "Device_Info;;" + pickled list containing dictionaries
        
        Request a listing of available audio channels to the specified instances
        memory. This message can be retrieved via instance.read_messages()"""
        channel_info = []
        for device in self.audio_devices:
            options = dict(**device.options)
            if options.has_key("stream_callback"):
                del options["stream_callback"] # can't pickle instancemethod Runtime_Decorator
            options["name"] = device.name
            options["sample_size"] = device.sample_size
            channel_info.append(options)
        channel_list = pickle.dumps(channel_info)
        self.send_to(listener._instance_name, "Channel_Info;;" + channel_list)
        
    def add_listener(self, listener, channel_name):
        channel = None
        for device in self.audio_devices:
            if channel_name in device.name:
                return self.listeners[device.name].append(listener._instance_name)
        
    def run(self):                                        
        # get the sound from each device and output it
        for device in self.audio_devices:
            device.next_frame()
            self._handle_device(device)            
        
        if self in self.parent.objects["Audio_Manager"]:
            Event("Audio_Manager", "run", component=self).post()

    def play_file(self, file_info, file, to=None, mute=False, record=False):
        options = {"data_source" : file, 
                   "mute" : mute,
                   "format" : file_info["format"]}
        info = {"defaultSampleRate" : file_info["rate"],
                "maxOutputChannels" : file_info["channels"],
                "name" : file_info["name"]}
        speaker = self.create(Audio_Output, info, **options)
        speaker.initialize()
        self.listeners[speaker.name] = []
        if to:
            self.listeners[speaker.name].append(to._instance_name)
            
    def play_wav_file(self, filename, to=None, mute=False):
        wav_file = self.create(Wav_File, filename=filename)
        info = {"defaultSampleRate" : wav_file.rate, "maxOutputChannels" : wav_file.channels, "name" : filename}
        options = {"format" : wav_file.format, "data_source" : wav_file, "mute" : mute}
        device = self.create(Audio_Output, info, **options)
        device.initialize()
        self.listeners[device.name] = []
        if to:
            self.listeners[filename].append(to._instance_name)
        
    def convert_to_stereo(self, mono_data):
        # interleave mostly the same data into a stereo signal
        mono = array.array("h", mono_data)
        stereo = array.array("h")
        for count, sample in enumerate(mono):
            stereo.append(sample)
            if sample:
                slightly_different = sample-1
            else:
                slightly_different = sample + 1
            slightly_different = sample-1
            stereo.append(slightly_different)
        return struct.pack("h"*len(stereo), *stereo)
     
    def convert_to_mono(self, stereo_data):
        return stereo_data[::2]
        
    def _handle_device(self, device):
        sound_chunk = device.data
        device.data = ''
        if sound_chunk:
            if device.record_to_disk: 
                #vv: print "%s recorded %s sound chunks" % (device.name, len(sound_chunk))
                device.file.writeframes(sound_chunk)    
        
            for client in self.listeners[device.name]:
                #vv: print "%s;; sent %s bytes of sound to %s" % (device.name, len(sound_chunk), client)
                self.send_to(client, "%s;;" % str(device.name) + sound_chunk)      