import pickle
import struct
import wave
import time
from contextlib import contextmanager
from sys import platform
from ctypes import CFUNCTYPE, c_int, c_char_p, cdll

# pyaudio requires: libportaudio0, libportaudio2, libportaudiocpp0, and portaudio19-dev on linux
# linux installation instructions:
# if installation was already attempted, do: sudo apt-get remove python-pyaudio
# wget http://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_i386.deb
# sudo dpkg -i python-pyaudio_0.2.8-1_i386.deb
import pyaudio
import base
import defaults
from eventlibrary import Event

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
        print "Please ignore any warnings you may have received"
    else:
        portaudio = pyaudio.PyAudio()
    print "...done"
    return portaudio
    
PORTAUDIO = initialize_portaudio()


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
        options["stream_callback"] = self.stream_callback
        return options
    options = property(_get_options)
    
    def _get_stream_callback(self):
        if getattr(self, "input"):
            callback = self._input_stream_callback
        else:
            callback = self._output_stream_callback
        return callback
    stream_callback = property(_get_stream_callback)
    
    def __init__(self, portaudio_device_info, *args, **kwargs):
        super(PyAudio_Device, self).__init__(*args, **kwargs)
        if portaudio_device_info["maxInputChannels"]:
            self.input = True         
            self.channels = int(portaudio_device_info["maxInputChannels"])   
            self.input_device = portaudio_device_info["index"]
        #if portaudio_device_info["maxOutputChannels"]:
        #     self.warning("Detected output channels on %s. Output channels not implemented, ignoring" % portaudio_device_info["name"])
        #    self.output = True
        #    self.channels = int(portaudio_device_info["maxOutputChannels"])
            #self.data_source
            
        self.rate = 48000 #int(portaudio_device_info["defaultSampleRate"])
        self.name = portaudio_device_info["name"]
        self.sample_size = PORTAUDIO.get_sample_size(pyaudio.paInt16)        
                
    def _get_data(self):
        return self.data_source.read(frames_per_buffer)
        
    def _input_stream_callback(self, in_data, frame_count, time_info, status):
        self.data = in_data
        return (in_data, pyaudio.paContinue)
    
    def _output_stream_callback(self, in_data, frame_count, time_info, status):
        return (self.data, pyaudio.paContinue)
        
    def _bind(self, output_device):
        """bind this input device to an output device such as a speaker"""
        self.output_stream = output_device.stream
        
    def _new_wave_file(self):
        """create a new wave file of appropriate format"""
        try:
            file = wave.open("%s recording.wav" % self.name, "wb")
        except IOError:
            print "unusable default filename %s" % (self.name)
            file = wave.open("%s.wav" % raw_input("Please enter filename: "), "wb")
        file.setnchannels(self.channels)
        file.setsampwidth(PORTAUDIO.get_sample_size(self.format))
        file.setframerate(self.rate)
        print "created wave file: channels %s, sample width %s, rate %s" % (self.channels, PORTAUDIO.get_sample_size(self.format), self.rate)
        return file
        
    def next_frame(self):
        next(self.thread)
        
    def _new_thread(self):
        stream = self.stream
        stream.start_stream()
        while self.active:
            yield
        stream.stop_stream()
        stream.close()

    def initialize(self):
        print "initializing device %s" % self.name
        try:
            self.stream = PORTAUDIO.open(**self.options)
        except:
            raise
        self.thread = self._new_thread()
        if self.recording:
            self.file = self._new_wave_file()  
        self.active = True    

        
class Audio_Configuration_Utility(base.Process):
        
    defaults = defaults.Audio_Configuration_Utility
    
    def __init__(self, *args, **kwargs):
        self.selected_devices = []
        super(Audio_Configuration_Utility, self).__init__(*args, **kwargs)
        
        if "default" in self.mode:
            default_input, default_output = self.get_default_devices()
            self.selected_devices.append(default_input)
            self.selected_devices.append(default_output)
            self.write_config_file(self.selected_devices)
            self.delete()
        else:
            self.all_devices = self.get_all_devices(self.mode)
            Event("Audio_Configuration_Utility", "run").post()
    
    def write_config_file(self, device_list):
        with open(self.config_file_name, "wb") as config_file:
            for device in device_list:
                print device["name"], device["maxInputChannels"], device["defaultSampleRate"]
            pickle.dump(device_list, config_file)
            config_file.flush()
            config_file.close()
            
    def get_all_devices(self, mode):
        all_devices = {}
        for device_number in xrange(PORTAUDIO.get_device_count()):
            device_info = PORTAUDIO.get_device_info_by_index(device_number)
            all_devices[device_number] = device_info
                       
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
                    device["index"] = index
                    self.selected_devices.append(device)
        print "finished selecting devices"        
    
    def get_default_devices(self):
        host_api_info = PORTAUDIO.get_default_host_api_info()
        default_input = PORTAUDIO.get_device_info_by_index(host_api_info["defaultInputDevice"])
        default_output = PORTAUDIO.get_device_info_by_index(host_api_info["defaultOutputDevice"])
        return (default_input, default_output)        
    
    def run(self):
        self.get_selections()
        self.write_config_file(self.selected_devices)
        self.delete()
        if getattr(self, "exit_when_finished", None):
            Event("System", "exit").post()

        
class Audio_Manager(base.Process):
    
    defaults = defaults.Audio_Manager
        
    def __init__(self, *args, **kwargs):
        self.channel_requests = []
        super(Audio_Manager, self).__init__(*args, **kwargs)
        try:
            self.load_config_file()       
        except:
            raise
            raw_input("Please run audio_config_utility. No config file found")
            Event("System", "exit").post()
        self.network_buffer = {}
        self.clients_listening_to = {}
        
        Event("Network_Manager", "create", "networklibrary.Server",
        incoming=self._incoming, outgoing=self._outgoing, on_connection=self._on_connection,
        name="Audio_Manager", port=40002, host_name="localhost").post()
        
    def _incoming(self, connection):
        self.network_buffer[connection] = connection.recv(2048)
        
    def _outgoing(self, connection, data):
        connection.send(data)

    def _on_connection(self, connection, address): # get which channel they want to listen to
        channel_info = []
        for device in self.objects["PyAudio_Device"]:
            options = dict(**device.options)
            del options["stream_callback"] # can't pickle instancemethod Runtime_Decorator
            options["name"] = device.name
            options["sample_size"] = device.sample_size
            options = pickle.dumps(options)
            channel_info.append(options)
        channel_list = "\r".join(channel_info)
        Event("Network_Manager", "buffer_data", connection, channel_list).post()
        self.channel_requests.append(connection)
        self.network_buffer[connection] = None
        
    def load_config_file(self):
        with open(self.config_file_name, "rb") as config_file:
            for device_info in pickle.load(config_file):
                device = self.create(PyAudio_Device, device_info)
                device.initialize()
            
    def run(self):
        # receive newly connected clients channel selection
        for connection in self.channel_requests:
            response = self.network_buffer[connection]
            if not response:
                pass
            else:
                self.channel_requests.remove(connection)
                for selection in response.split("\n"):
                    device = self.objects["PyAudio_Device"][int(selection)]
                    device.network_listeners = True
                    try:
                        self.clients_listening_to[device.name].append(connection)
                    except KeyError:
                        self.clients_listening_to[device.name] = []
                        self.clients_listening_to[device.name].append(connection)
                                        
        # get the sound from each device and output it
        for device in self.objects["PyAudio_Device"]:
            device.next_frame()
            self._handle_device(device)            
        
        if self in self.parent.objects["Audio_Manager"]:
            Event("Audio_Manager", "run").post()
            
    def _handle_device(self, device):
        if device.input and device.data:
            sound_chunk = device.data
            device.data = ""
            #for listener in device.listeners:
             #   listener.write(sound_chunk)
            if device.recording: #
                device.file.writeframes(sound_chunk)
            if device.network_listeners:
                #sound_chunk = struct.pack("4096s", sound_chunk)
                for client in self.clients_listening_to[device.name]:
                    Event("Network_Manager", "buffer_data", client, sound_chunk).post()    
        elif device.output:
            device.data = device._get_data()