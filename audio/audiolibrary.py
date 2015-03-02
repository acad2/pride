import array
import pickle
import struct
import wave
import sys
import atexit

import mpre.base as base
import mpre.vmlibrary as vmlibrary
import defaults
from mpre.utilities import Latency
Instruction = base.Instruction

# supports both pyalsaaudio (linux) and pyaudio (cross platform)
if "linux" in sys.platform:
    import alsaaudiodevices as audio_devices
    alsaaudio = audio_devices.alsaaudio
    default_input, default_output = "hw:0,0", "hw:0,0"
    DEVICES = dict((index, {"card" : "hw:{0},0".format(index), "name" : device_name}) for index,  device_name in enumerate(alsaaudio.cards()))    
    default_input = DEVICES[0]
    default_output = DEVICES[0]
    
else:
    import portaudiodevices as audio_devices
    pyaudio = audio_devices.pyaudio
    PORTAUDIO = audio_devices.PORTAUDIO
    
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
    
    DEVICES = {}
    for device_number in xrange(PORTAUDIO.get_device_count()):
        device_info = PORTAUDIO.get_device_info_by_index(device_number)
        options = {"channels" : max(device_info["maxOutputChannels"], device_info["maxInputChannels"]),
                   "rate" : int(device_info["defaultSampleRate"]),
                   "name" : device_info["name"]}
        DEVICES[device_number] = options        

Audio_Device = audio_devices.Audio_Device
Audio_Input = audio_devices.Audio_Input
Audio_Output = audio_devices.Audio_Output


class Wav_File(base.Base):

    defaults = defaults.Wav_File

    def _get_audiosize(self):
        return self.channels * self.sample_width * self.file.getnframes()
    audio_size = property(_get_audiosize)
    
    def __init__(self, **kwargs):
        super(Wav_File, self).__init__(**kwargs)
        
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

    def read(self, size=0):
        size = size if size else self.audio_size
        
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


class Audio_Configuration_Utility(vmlibrary.Process):

    defaults = defaults.Audio_Configuration_Utility

    def __init__(self, **kwargs):
        self.selected_devices = []
        super(Audio_Configuration_Utility, self).__init__(**kwargs)

        if "default" in self.mode:
            self.selected_devices.append(default_input)
            self.selected_devices.append(default_output)
            self.write_config_file(self.selected_devices)
            self.delete()
        else:
            self.run_instruction.execute(self.priority)

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

        while "done" not in selection:
            print "\n"*80
            print "type 'done' to finish selecting..."
            print "**************************************"
            self.print_display_devices(DEVICES)
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
                    device = DEVICES[index]
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
        self.delete()
        if getattr(self, "exit_when_finished", None):
            exit()


class Audio_Manager(vmlibrary.Process):

    defaults = defaults.Audio_Manager

    def _get_devices(self):
        return self.objects.get("Audio_Input", []) + self.objects.get("Audio_Output", [])

    audio_devices = property(_get_devices)

    def __init__(self, **kwargs):
        device_names = self.device_names = {}
        super(Audio_Manager, self).__init__(**kwargs)
                
        if self.use_defaults:
            self.load_default_devices()
            
        if self.config_file_name:
            try:
                self.load_config_file()
            except IOError:
                response = raw_input("No audio config file found\nlaunch Audio_Config_Utility?: (y/n) ").lower()
                if 'y' in response:
                    Instruction("System", "create", Audio_Configuration_Utility,        
                                exit_when_finished=False).execute

    def load_default_devices(self):
        input = self.create(Audio_Input, **default_input)
        output = self.create(Audio_Output, **default_output)
        
        device_names = self.device_names
        device_names[input.instance_name] = input
        device_names["Microphone"] = input
        
        device_names[output.instance_name] = output
        device_names["Speakers"] = output
        
    def load_config_file(self):
        with open(self.config_file_name, "rb") as config_file:
            for device_info in pickle.load(config_file):
                device = self.create(Audio_Input, **device_info)
                self.device_names[device.instance_name] = device
                self.device_names[device.name] = device
                
    def send_channel_info(self, sender, packet):
        """usage: Instruction("Audio_Manager", "send_channel_info", my_object).execute()
        => Message: "Device_Info;;" + pickled list containing dictionaries

        Request a listing of available audio channels to the specified instances
        memory. This message can be retrieved via instance.read_messages()"""
        channel_info = []
        for device in self.audio_devices:
            options = dict(**device.options)
            del options["start"]
            options["name"] = device.name
            options["device_name"] = device.instance_name
            options["sample_size"] = device.sample_size
            channel_info.append(options)
        channel_list = pickle.dumps(channel_info)
        self.reaction(sender, "handle_channel_info " + channel_list)

    def run(self):
        for device in self.objects["Audio_Input"]:
            device.get_data()
        self.run_instruction.execute(self.priority)

   # def handle_delay(self, instance):
        
        
    def play_file(self, file, to=None, mute=False):
        _format = file.format # in bytes, pyaudio needs it's own constant instead
        try:
            format_name = PORTAUDIO.format_mapping[_format]
            constant = getattr(pyaudio, format_name)
            _format = constant
            sample_size = int(format_name[-2:])
        except NameError:
            pass
        file_data = file.read()
        file_size = len(file_data)
        options = {"data_source" : file_data,
                   "available" : file_size,
                   "format" : _format,
                   "rate" : file.rate,
                   "channels" : file.channels,
                   "name" : file.filename}
        
        speaker = self.create(Audio_Output, **options)
        speaker.source_name = file.instance_name
        speaker.mute = mute
        
        if to:
            speaker.add_listener(to, to, True)
   
    def record(self, device_name, file, channels=2, rate=48000):  
        device_name = self.device_names[device_name].instance_name
        recording = self.create(Audio_Output, source_name=device_name,
                                              name="{}_recording".format(device_name),
                                              file=file, 
                                              channels=channels,
                                              rate=rate)


class Audio_Channel(base.Base):

    defaults = defaults.Audio_Channel

    def __init__(self, **kwargs):
        super(Audio_Channel, self).__init__(**kwargs)
       
    def handle_audio(self, sender, audio):
        self.audio_data = audio
        
    def read(self, bytes=0):
        if not bytes:
            bytes = len(self.audio_data)
        data = self.audio_data[:bytes]
        self.audio_data[bytes:]
        return data


class Audio_Service(base.Base):

    defaults = defaults.Audio_Service

    def _get_channels(self):
        return self.objects["Audio_Channel"]
    channels = property(_get_channels)

    def __init__(self, **kwargs):
        super(Audio_Service, self).__init__(**kwargs)
        self.objects["Audio_Channel"] = []
        self.reaction("Audio_Manager", "send_channel_info " + self.instance_name)

    def handle_channel_info(self, sender, packet):
        channel_configuration = pickle.loads(packet)
        for channel_info in channel_configuration:
            device_name = channel_info["device_name"]
                        
            channel = self.create(Audio_Channel, **channel_info)
            self.reaction(device_name, "add_listener " + channel.instance_name)