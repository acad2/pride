# pyaudio requires: libportaudio0, libportaudio2, libportaudiocpp0, and portaudio19-dev on linux
# linux installation instructions:
# if installation was already attempted, do: sudo apt-get remove python-pyaudio
# wget http://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_i386.deb
# sudo dpkg -i python-pyaudio_0.2.8-1_i386.deb
import wave
import sys
import mmap
from contextlib import contextmanager
from ctypes import *

import pyaudio

import mpre.base as base
import mpre.vmlibrary as vmlibrary
from mpre.utilities import Latency
import defaults
Instruction = base.Instruction

FormatError = type("FormatError", (BaseException, ), {})

@contextmanager
def _alsa_errors_suppressed():
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

def _initialize_portaudio():
    print "initializing PortAudio..."
    if "linux" in sys.platform:
        print "Trying to suppress ALSA configuration errors..."
        with _alsa_errors_suppressed():
            portaudio = pyaudio.PyAudio()
        print "**Please ignore any warnings you may have received**"
    else:
        portaudio = pyaudio.PyAudio()
    print "...done"
    return portaudio

PORTAUDIO = _initialize_portaudio()

PORTAUDIO.format_mapping = {1 : "paInt8",
                            2 : "paInt16",
                            3 : "paInt24",
                            4 : "paInt32"}
                            
def _formats_to_indices():
    format_lookup = {}
    for device_index in range(PORTAUDIO.get_device_count()):
        device_info = PORTAUDIO.get_device_info_by_index(device_index)
        rate = device_info["defaultSampleRate"]
        
        channels = device_info["maxInputChannels"]
        if channels:
            in_or_out = "input"
        else:
            channels = device_info["maxOutputChannels"]
            in_or_out = "output"
        
        try:
            format_lookup[(rate, channels, in_or_out)].append(device_info["index"])
        except KeyError:
            format_lookup[(rate, channels, in_or_out)] = [device_info["index"]]
    return format_lookup
    
format_lookup = _formats_to_indices()
           
class Audio_Device(base.Reactor):

    defaults = defaults.PyAudio_Device
    possible_options = ("rate", "channels", "format", "input", "output",                    "input_device_index", "output_device_index",                    "frames_per_buffer", "start", "stream_callback",
                        "input_host_api_specific_stream_info",
                        "output_host_api_specific_stream_info")
                        
    # properties are calculated attributes
    def _get_options(self):
        options = {}
        for option in self.possible_options:
            value = getattr(self, option, None)
            if value:
                options[option] = value
        
        return options
    options = property(_get_options)

    def _get_full_buffer_size(self):
        return self.channels * self.frames_per_buffer * self.sample_size
    full_buffer_size = property(_get_full_buffer_size)
        
    def __init__(self, **kwargs):
        self.listeners = []
        self.local_listeners = set()
        self.available = 0
        self._format_error = "{}hz {} channel {} not supported by any api"
        self.sample_size = PORTAUDIO.get_sample_size(pyaudio.paInt16)
        super(Audio_Device, self).__init__(**kwargs)
                
    def open_stream(self):
        return PORTAUDIO.open(**self.options)
    
    def add_listener(self, sender, packet):
        if sender in self.environment.Component_Resolve:
            self.local_listeners.add(sender)
            self.listeners.append(sender)
        else:
            self.listeners.append((packet, sender))
                
    def handle_audio(self, sender, packet):
        available = len(packet)
        self.available += available
        self.data_source += packet
        
    def _new_thread(self):
        raise NotImplementederror
        
    def get_data(self):
        raise NotImplementedError

    def handle_data(self, audio_data):
        for client in self.listeners:
            scope = "local" if client in self.local_listeners else "network"
            self.reaction(client, "handle_audio " + audio_data, scope=scope)

            
class Audio_Input(Audio_Device):

    defaults = defaults.Audio_Input

    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)
        
        if not hasattr(self, "input_device_index"):
            try:
                self.input_device_index = format_lookup[(self.rate, self.channels, "input")][0]
            except KeyError:
                raise FormatError(self._format_error.format(self.rate, self.channels, "input"))
       
        self.thread = self._new_thread()
                    
    def _new_thread(self):
        stream = self.open_stream()
        get_read_available = stream.get_read_available
        
        data_source = self.data_source if self.data_source else stream
        read_stream = data_source.read
        handle_data = self.handle_data

        if data_source is not stream:
            byte_scalar = self.sample_size * self.channels
        else:
            byte_scalar = 1
            
        frames_per_buffer = self.frames_per_buffer
        full_buffer_size = self.full_buffer_size
        frame_counter = self.frame_count
        _data = ''

        while True:            
            frame_count = get_read_available()
            data = read_stream(frame_count * byte_scalar)
            _data += data
            frame_counter += frame_count
            
            if frame_counter >= frames_per_buffer:
                frame_counter -= frames_per_buffer
                handle_data(_data[:full_buffer_size])
                self._data = _data = _data[full_buffer_size:]
            yield

    def get_data(self):
        return next(self.thread)


class Audio_Output(Audio_Device):

    defaults = defaults.Audio_Output

    def __init__(self, **kwargs):
        super(Audio_Output, self).__init__(**kwargs)
        
        if not hasattr(self, "output_device_index"):
            try:
                self.output_device_index = format_lookup[(self.rate, self.channels, "output")][0]
            except KeyError:
                raise FormatError(self._format_error.format(self.rate, self.channels, "output"))        
        
        if not self.source_name:
            print "no source supplied"
            self.mute = True
        else:
            print "adding {} to {}".format(self.instance_name, self.source_name)
            self.reaction(self.source_name, "add_listener " + self.instance_name)
        from mpre.utilities import Latency
        self.latency = Latency(name="incoming_audio")
        self.latency.update()
       # self.thread = self._new_thread()
        self.stream = self.open_stream()
        
    def _new_thread(self):
        byte_scalar = self.sample_size * self.channels
                
        frames_per_buffer = self.frames_per_buffer
        full_write_buffer = byte_scalar * frames_per_buffer
        silence = "\x00" * full_write_buffer

        handle_data = self.handle_data
                                       
        while True:            
            number_of_frames = get_write_available()
            if number_of_frames >= frames_per_buffer:
                if not self.available:
                    self.alert("Buffer underflow", level=0)
                    yield                    
                    continue

                byte_count = byte_scalar * frames_per_buffer
                audio_data = silence if self.mute else self.data_source[:byte_count]
                
                self.data_source = self.data_source[byte_count:]
                self.available -= byte_count
                
                # reaction listeners here
                handle_data(audio_data)
                # write to device/file here
                stream_write(audio_data)
                
            yield

    def handle_audio(self, sender, packet):
        self.latency.update()
        self.latency.display()
        self.available += len(packet)
        self.data_source += packet
       
    def write_audio(self):
        number_of_frames = self.stream.get_write_available()
       # self.alert("{} bytes available; {} frames available; {} frames per buffer",
        #           (self.available, number_of_frames, self.frames_per_buffer),
         #          level=0)
        if number_of_frames >= self.frames_per_buffer:        
            byte_count = min(self.available, self.full_buffer_size)
            audio_data = ('\x00' * byte_count if self.mute else 
                          self.data_source[:byte_count])
            
            self.data_source = self.data_source[byte_count:]
            self.available -= byte_count
            # reaction listeners here
            self.handle_data(audio_data)
            # write to device/file here
            self.stream.write(audio_data) 
     #   else:
            #Instruction("Audio_Manager", "handle_delay").execute()