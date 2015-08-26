import pickle
import wave
import sys
import os

import mpre
import mpre.base as base
import mpre.vmlibrary as vmlibrary
import mpre.fileio as fileio
from mpre.utilities import Latency
Instruction = mpre.Instruction
objects = mpre.objects

# supports both pyalsaaudio (linux) and pyaudio (cross platform)
   
def record_wav_file(parse_args=False, **kwargs):
    audio_manager = objects["Audio_Manager"]
    print "Creating wav file: ", kwargs
    wav_file = audio_manager.create("mpre.audio.audiolibrary.Wav_File",
                                    parse_args=parse_args, mode='wb', **kwargs)
    audio_manager.record("Microphone", file=wav_file)
    return wav_file
    
def wav_file_info(parse_args=True, **kwargs):
    wav_file = Wav_File(parse_args=parse_args, **kwargs)
    
    print "{} information: ".format(wav_file.filename)
    for attribute in ("rate", "channels", "format", 
                      "sample_width", "number_of_frames"):
        print "{}: {}".format(attribute, getattr(wav_file, attribute))
        
class Audio_Reactor(base.Base):
    
    defaults = base.Base.defaults.copy()
    defaults.update({"source_name" : ''})
    
    def __init__(self, **kwargs):
        self.listeners = []
        super(Audio_Reactor, self).__init__(**kwargs)
        if self.source_name:
            objects[self.source_name].add_listener(self.instance_name)
            
    def set_input_device(self, target_instance_name):
        self.alert("Setting input device to {}".format(target_instance_name),
                   level='v')
        if self.source_name:
            objects[self.source_name].remove_listener(self.instance_name)
            self.source_name = None
        
        if target_instance_name:
            objects[target_instance_name].add_listener(self.instance_name)
            self.source_name = target_instance_name
            
    def handle_audio_input(self, audio_data):
        self.handle_audio_output(audio_data)
        
    def handle_audio_output(self, audio_data):
        for client in self.listeners:
            objects[client].handle_audio_input(audio_data)
    
    def handle_end_of_stream(self):
        self.alert("end of stream")
                
    def add_listener(self, instance_name):
        self.listeners.append(instance_name)
            
    def remove_listener(self, instance_name):
        self.listeners.remove(instance_name)    
                    

class Wav_File(Audio_Reactor):

    defaults = Audio_Reactor.defaults.copy()
    defaults.update({"mode" : "rb",
                     "filename" : "",
                     "repeat" : False,
                     "channels" : 2,
                     "rate" : 48000,
                     "sample_width" : 2})

    def _get_audiosize(self):
        return self.channels * self.sample_width * self.file.getnframes()
    audio_size = property(_get_audiosize)
    
    def __init__(self, **kwargs):
        super(Wav_File, self).__init__(**kwargs)
        print "inside wav file: ", self.filename
        self.name = os.path.split(self.filename)[-1].split('.', 1)[0]
        
        _file = self.file = wave.open(self.filename, self.mode)
        if 'r' in self.mode:
            channels, sample_width, rate, number_of_frames, comptype, compname = self.file.getparams()
                
            self.channels = channels
            self.sample_width = sample_width
            self.format = 2 # hardcoded to PCM_FORMAT_S16_LE for quick fix
            self.rate = rate
            self.number_of_frames = number_of_frames
            self.comptype = comptype
            self.compname = compname
        else:
            _file.setparams((self.channels, self.sample_width, self.rate, 0, 'NONE', 'not compressed'))
            
        message = "opened wav file with channels: {0}, format: {1}, rate: {2}"
        self.alert(message, (self.channels, self.sample_width, self.rate), level="vv")
            
    def read(self, size=None): # accepts size in bytes and converts to frame count   
        size = (size / 4) if size is not None else (self.audio_size / 4)
        
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

    def handle_audio_input(self, audio_input):
        self.write(audio_input)
        

class Config_Utility(vmlibrary.Process):

    defaults = vmlibrary.Process.defaults.copy()
    defaults.update({"config_file_name" : "audiocfg",
                     "mode" : ("input",),
                     "running" : False})

    def __init__(self, **kwargs):
        self.selected_devices = []
        super(Config_Utility, self).__init__(**kwargs)

        if "default" in self.mode:
            self.selected_devices.append(self.default_input)
            self.selected_devices.append(self.default_output)
            self.write_config_file(self.selected_devices)
            Instruction(self.instance_name, "delete").execute()
        else:
            self.run()
            
    def write_config_file(self, device_list):
        with open(self.config_file_name, "wb") as config_file:
            for device in device_list:
                print device
            pickle.dump(device_list, config_file)
            config_file.flush()
            config_file.close()

    def print_display_devices(self, device_dict):
        for key, value in device_dict.items():
            print "%s: %s" % (key, value)

    def get_selections(self):
        selection = ""
        self.selected_devices = []
        devices = self.devices
        
        while "done" not in selection:
            print "\n"*80
            print "type 'done' to finish selecting..."
            print "**************************************"
            self.print_display_devices(devices)
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
                    device = devices[index]
                except KeyError:
                    selection = raw_input("Invalid index. press enter to continue to or 'done' to finish")
                    if 'done' in selection:
                        break
                else:
                    name = raw_input("Rename device or press enter for default name: ")
                    if name:
                        device["name"] = name
                                   
                    self.selected_devices.append(device)
        print "finished selecting devices"
                                    
    def run(self):
        self.get_selections()
        self.write_config_file(self.selected_devices)
        
        if getattr(self, "exit_when_finished", None):
            exit()
        else:
            Instruction(self.instance_name, "delete").execute()

            
class Audio_Manager(base.Base):

    defaults = base.Base.defaults.copy()
    defaults.update({"config_file_name" : '',
                     "use_defaults" : True,
                     "configure" : False})

    def _get_devices(self):
        return self.objects.get("Audio_Input", []) + self.objects.get("Audio_Output", [])

    audio_devices = property(_get_devices)

    def __init__(self, **kwargs):
        device_names = self.device_names = {}
        super(Audio_Manager, self).__init__(**kwargs)
        self.objects.setdefault("Audio_Input", [])
        
        self.load_api()
        
        if self.configure:
            self.run_configuration()
            
        if self.use_defaults:
            self.load_default_devices()
            
        if self.config_file_name:
            try:
                self.load_config_file()
            except IOError:
                response = raw_input("No audio config file found\nlaunch Audio_Config_Utility?: (y/n) ").lower()
                if 'y' in response:
                    self.run_configuration()

        self.alert("Finished loading", level='v')
        
    def run_configuration(self, exit_when_finished=False):
        self.create(Config_Utility,
                    default_input=self.default_input,
                    default_output=self.default_output,
                    devices=self.devices)
        
        if exit_when_finished:
            Instruction("Metapython", "exit").execute()
        
    def load_api(self):
        if "linux" in sys.platform:
            import alsaaudiodevices as audio_devices
            self.api = 'alsaaudio'
            
            default_input, default_output = "hw:0,0", "hw:0,0"
            devices = dict((index, {"card" : "hw:{0},0".format(index), 
                                    "name" : device_name}) for 
                                    index,  device_name in 
                                    enumerate(audio_devices.alsaaudio.cards()))    
            self.default_input = devices[0]
            self.default_output = devices[0]
            self.devices = devices
        else:
            import portaudiodevices as audio_devices
            self.api = 'portaudio'
            self.pyaudio = audio_devices.pyaudio
            PORTAUDIO = self.portaudio = audio_devices.PORTAUDIO
            
            host_api_info = PORTAUDIO.get_default_host_api_info()
            input_index = host_api_info["defaultInputDevice"]
            output_index = host_api_info["defaultOutputDevice"]
            
            default_input = PORTAUDIO.get_device_info_by_index(input_index)
            default_output = PORTAUDIO.get_device_info_by_index(output_index)
            
            default_input["input_device_index"] = input_index
            default_input["rate"] = int(default_input["defaultSampleRate"])
            default_input["channels"] = default_input["maxInputChannels"]

            default_output["output_device_index"] = output_index
            default_output["rate"] = int(default_input["defaultSampleRate"])
            default_output["channels"] = default_input["maxInputChannels"]
            
            self.devices = devices = {}
            for device_number in xrange(PORTAUDIO.get_device_count()):
                device_info = PORTAUDIO.get_device_info_by_index(device_number)
                options = {"channels" : max(device_info["maxOutputChannels"], device_info["maxInputChannels"]),
                        "rate" : int(device_info["defaultSampleRate"]),
                        "name" : device_info["name"]}
                devices[device_number] = options        
        
            self.default_input = default_input
            self.default_output = default_output
            
        self.Audio_Device = audio_devices.Audio_Device
        self.Audio_Input = audio_devices.Audio_Input
        self.Audio_Output = audio_devices.Audio_Output
    
    def load_default_devices(self):
        input = self.create(self.Audio_Input, **self.default_input)
        output = self.create(self.Audio_Output, **self.default_output)
        
        device_names = self.device_names
        device_names[input.instance_name] = input
        device_names["Microphone"] = input
        
        device_names[output.instance_name] = output
        device_names["Speakers"] = output
        
    def load_config_file(self):
        with open(self.config_file_name, "rb") as config_file:
            for device_info in pickle.load(config_file):
                device = self.create(self.Audio_Input, **device_info)
                self.device_names[device.instance_name] = device
                self.device_names[device.name] = device
                         
    def get_devices(self, devices="Audio_Input"):
        return [(instance.name, instance.instance_name) for 
                instance in self.objects[devices]]
                        
    def record(self, device_name, file):  
        device_name = self.device_names[device_name].instance_name
        file.set_input_device(device_name)
        