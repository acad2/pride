#   mpf.audiolibrary - create an audio api for the metaprogramming framework vm
#
#    Copyright (C) 2014  Ella Rose
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import array
import pickle
import struct
import wave
import time
from contextlib import contextmanager
from sys import platform, exit
from ctypes import CFUNCTYPE, c_int, c_char_p, cdll

# pyaudio requires: libportaudio0, libportaudio2, libportaudiocpp0, and portaudio19-dev on linux
# linux installation instructions:
# if installation was already attempted, do: sudo apt-get remove python-pyaudio
# wget http://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_i386.deb
# sudo dpkg -i python-pyaudio_0.2.8-1_i386.deb
import pyaudio

import base
import defaults
Event = base.Event

@contextmanager
def alsa_errors_suppressed():
    prototype = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def do_nothing(filename, line, function, error, format):
        return
    c_suppression_function = prototype(do_nothing)
    try:
        alsa = cdll.LoadLibrary("libasound.so")
    except OSError:
        alsa = cdll.LoadLibrary("libasound.so.2")
    alsa.snd_lib_error_set_handler(c_suppression_function)
    yield
    alsa.snd_lib_error_set_handler(None)
 
def initialize_portaudio(): 
    print "initializing PortAudio..."
    if "linux" in platform:
        print "Trying to suppress ALSA configuration errors..."
        with alsa_errors_suppressed():
            portaudio = pyaudio.PyAudio()
        print "**Please ignore any warnings you may have received**"
    else:
        portaudio = pyaudio.PyAudio()
    print "...done"
    return portaudio
    
PORTAUDIO = initialize_portaudio()


class Wav_File(base.Base):
    
    defaults = defaults.Wav_File
    
    def __init__(self, **kwargs):
        super(Wav_File, self).__init__(**kwargs)
        self.file = wave.open(self.filename, "rb")
        channels, sample_width, rate, number_of_frames, comptype, compname = self.file.getparams()
        format = PORTAUDIO.get_format_from_width(sample_width)
        self.channels = channels
        self.sample_width = sample_width
        self.format = format
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
        
        
class PyAudio_Device(base.Base):
    
    defaults = defaults.PyAudio_Device
    possible_options = ("rate", "channels", "format", "input", "output", "input_device_index",
    "output_device_index", "frames_per_buffer", "start", "input_host_api_specific_stream_info",
    "output_host_api_specific_stream_info", "stream_callback")
    # properties are calculated attributes
    def _get_options(self):
        options = {}
        for option in self.possible_options:
            value = getattr(self, option, None)
            if value:
                options[option] = value
        #options["stream_callback"] = self.stream_callback
        return options
    options = property(_get_options)
    
    def __init__(self, portaudio_device_info, **kwargs):
        super(PyAudio_Device, self).__init__(**kwargs)            
        self.rate = int(portaudio_device_info["defaultSampleRate"])
        self.name = portaudio_device_info["name"]
        self.sample_size = PORTAUDIO.get_sample_size(pyaudio.paInt16)
        if portaudio_device_info.has_key("index"):
            self.index = portaudio_device_info["index"]
        
    def initialize(self):
        #v: print "initializing device %s" % self.name, self.options
        try:
            self.stream = PORTAUDIO.open(**self.options)
        except:
            raise
        self.thread = self._new_thread()
        if self.record_to_disk:
            self.file = self._new_wave_file()  
        self.active = True   
        
    def _open_wave_file(self, filename):
        return wave.open(filename, "rb")
        
    def _new_wave_file(self):
        """create a new wave file of appropriate format"""
        filename = ("%s recording.wav" % self.name).replace(" ", "_")
        try:
            file = wave.open(filename, "wb")
        except IOError:
            print "unusable default filename %s" % (self.name)
            file = wave.open("%s.wav" % raw_input("Please enter filename: "), "wb")
        file.setnchannels(self.channels)
        file.setsampwidth(PORTAUDIO.get_sample_size(self.format))
        file.setframerate(48000)
        print "created wave file: channels %s, sample width %s, rate %s" % (self.channels, PORTAUDIO.get_sample_size(self.format), self.rate)
        return file
        
    def next_frame(self):
        try:
            next(self.thread)
        except StopIteration:
            self.delete()
            
    def _new_thread(self):
        raise NotImplementedError
        """stream = self.stream
        stream.start_stream()
        while stream.is_active():
            yield
        stream.stop_stream()
        stream.close()"""
 

class Audio_Input(PyAudio_Device):
       
    defaults = defaults.Audio_Input
    
    def __init__(self, portaudio_device_info, **kwargs):
        super(Audio_Input, self).__init__(portaudio_device_info, **kwargs)
        self.channels = portaudio_device_info["maxInputChannels"]
        self.input_device_index = self.index
    
    def _new_thread(self):
        stream = self.stream
        while self.active:
            #if stream.get_read_available() >= self.frames_per_buffer:
                #print "removing %s of available %s frames" % (self.frames_per_buffer, stream.get_read_available())
            self.data = stream.read(self.frames_per_buffer)#stream.get_read_available())
            yield   
    
    #def stream_callback(self, in_data, frame_count, time_info, status):
    #    self.data = in_data
    #    return (in_data, pyaudio.paContinue)
            

class Audio_Output(PyAudio_Device):
            
    defaults = defaults.Audio_Output

    def __init__(self, portaudio_device_info, **kwargs):
        super(Audio_Output, self).__init__(portaudio_device_info, **kwargs)
        self.channels = portaudio_device_info["maxOutputChannels"]
        
        if hasattr(self, "index"):
            self.output_device_index = self.index
         
        if not self.data_source:
            self.mute = True
            
    def set_source(self, file_like_object):
        self.data_source = file_like_object
        
    def _new_thread(self):
        stream = self.stream
        while self.active:
            number_of_frames = stream.get_write_available()
            #print "%s frames available, fpb: %s" % (number_of_frames, self.frames_per_buffer)
            if number_of_frames >= self.frames_per_buffer:
                data = self.data_source.read(self.frames_per_buffer)
                self.data = data
                if self.mute:
                    data = "\x00" * self.frames_per_buffer
                stream.write(data)
                yield
            
    """def _new_thread(self):
        self.stream.start_stream()
        while self.stream.is_active():
            yield
        self.stream.stop_stream()
        self.stream.close()
        
    def stream_callback(self, in_data, frame_count, time_info, status):
        data = self.data = self.data_source.read(frame_count)
        if self.mute:
            data = "\x00" * len(data)
        return (data, pyaudio.paContinue)"""
            
        
class Audio_Configuration_Utility(base.Process):
        
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
                print device["name"], device["maxInputChannels"], device["defaultSampleRate"]
            pickle.dump(device_list, config_file)
            config_file.flush()
            config_file.close()
            
    def get_all_devices(self):
        all_devices = {}
        count = 0
        for device_number in xrange(PORTAUDIO.get_device_count()):
            device_info = PORTAUDIO.get_device_info_by_index(device_number)
            all_devices[device_number] = device_info
            count += 1
        return all_devices

    def print_display_devices(self, device_dict):
        for key, value in device_dict.items():
            print "%s: %s" % (key, value["name"])
        
    def get_selections(self):
        selection = ""
        self.selected_devices = []
    
        while "done" not in selection:
            print "\n"*80
            print "type 'done' to finish selecting..."
            print "**************************************"
            self.print_display_devices(self.all_devices)
            print "currently using: ", [item["name"] for item in self.selected_devices]
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
        host_api_info = PORTAUDIO.get_default_host_api_info()
        default_input = PORTAUDIO.get_device_info_by_index(host_api_info["defaultInputDevice"])
        default_output = PORTAUDIO.get_device_info_by_index(host_api_info["defaultOutputDevice"])
        return (default_input, default_output)        
    
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
            input_info, output_info = Audio_Configuration_Utility.get_default_devices()
            input = self.create(Audio_Input, input_info)
            output = self.create(Audio_Output, output_info)
            input.initialize()
            output.initialize()
            self.listeners[input.name] = []
            self.listeners[output.name] = []
    
    def load_config_file(self):
        with open(self.config_file_name, "rb") as config_file:
            for device_info in pickle.load(config_file):
                device = self.create(Audio_Input, device_info)
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