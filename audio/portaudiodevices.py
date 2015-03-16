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
import mpre.audio.audiolibrary as audiolibrary
from mpre.utilities import Latency

import mpre.audio.defaults as defaults
Instruction = base.Instruction

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
           
class Audio_Device(audiolibrary.Audio_Reactor):

    defaults = defaults.PyAudio_Device
    possible_options = ("rate", "channels", "format", "input", "output",                    "input_device_index", "output_device_index",                    "frames_per_buffer", "start", "stream_callback",
                        "input_host_api_specific_stream_info",
                        "output_host_api_specific_stream_info")
                        
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
        self.available = 0
        self._format_error = "{}hz {} channel {} not supported by any api"
        self.sample_size = PORTAUDIO.get_sample_size(pyaudio.paInt16)
        super(Audio_Device, self).__init__(**kwargs)
                
    def open_stream(self):
        return PORTAUDIO.open(**self.options)
   
    def mute(self):
        if self.is_muted:
            self.data_source = '\x00' * self.full_buffer_size
            self.is_muted = True
        else:
            self.is_muted = False
        
    def get_data(self):
        raise NotImplementedError

            
class Audio_Input(Audio_Device):

    defaults = defaults.Audio_Input

    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)
        
        if not hasattr(self, "input_device_index"):
            try:
                self.input_device_index = format_lookup[(self.rate, self.channels, "input")][0]
            except KeyError:
                raise FormatError(self._format_error.format(self.rate, self.channels, "input"))
       
        stream = self.stream = self.open_stream()
        if not self.data_source:
            self.data_source = stream
        
    def get_data(self):     
        stream = self.stream
        frame_count = stream.get_read_available()
        data_source = self.data_source
        data = self.data
        
        if data_source is stream:
            frame_count = min(frame_count, self.frames_per_buffer)
            old_size = len(data)
            data += data_source.read(frame_count)
            byte_count = len(data) - old_size
        else:
            byte_count = max((frame_count * self.sample_size * self.channels),
                              self.full_buffer_size)
            data += data_source.read(byte_count)
                        
        self.handle_audio_output(data[:byte_count])
        self.data = data[byte_count:]    
        
        
class Audio_Output(Audio_Device):

    defaults = defaults.Audio_Output

    def __init__(self, **kwargs):
        super(Audio_Output, self).__init__(**kwargs)
        
        if not hasattr(self, "output_device_index"):
            try:
                self.output_device_index = format_lookup[(self.rate, self.channels, "output")][0]
            except KeyError:
                raise FormatError(self._format_error.format(self.rate, self.channels, "output"))        
        
        self.stream = self.open_stream()
                 
    def handle_audio_input(self, sender, audio_data):
        self.data_source += audio_data
        available = self.available = len(self.data_source)
                   
        number_of_frames = self.stream.get_write_available()

        byte_count = min(number_of_frames * self.channels * self.sample_size,
                         available)
                         
        output_data = self.data_source[:byte_count]
                
        self.handle_audio_output(output_data)
        self.stream.write(output_data)
        
        if not self.is_muted:
            self.data_source = self.data_source[byte_count:]               
            self.available -= byte_count