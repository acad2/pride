# pyaudio requires: libportaudio0, libportaudio2, libportaudiocpp0, and portaudio19-dev on linux
# linux installation instructions:
# if installation was already attempted, do: sudo apt-get remove python-pyaudio
# wget http://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_i386.deb
# sudo dpkg -i python-pyaudio_0.2.8-1_i386.deb
import wave
import sys
from contextlib import contextmanager

import pyaudio

import base
import defaults

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
    if "linux" in sys.platform:
        print "Trying to suppress ALSA configuration errors..."
        with alsa_errors_suppressed():
            portaudio = pyaudio.PyAudio()
        print "**Please ignore any warnings you may have received**"
    else:
        portaudio = pyaudio.PyAudio()
    print "...done"
    return portaudio
    
PORTAUDIO = initialize_portaudio()
PORTAUDIO.format_mapping = {1 : "paInt8",
                            2 : "paInt16",
                            3 : "paInt24",
                            4 : "paInt32"}
                            
class Audio_Device(base.Base):
    
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
    
    def _get_full_buffer_size(self):
        return self.channels * self.frames_per_buffer * self.sample_size
    full_buffer_size = property(_get_full_buffer_size)
    
    def __init__(self, **kwargs):
        super(Audio_Device, self).__init__(**kwargs)            
        self.sample_size = PORTAUDIO.get_sample_size(pyaudio.paInt16)
        
    def initialize(self):
        self.alert("initializing device {0} with options: {1}".format(self.name, self.options), 2)
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
        file.setframerate(self.rate)
        print "created wave file: channels %s, sample width %s, rate %s" % (self.channels, PORTAUDIO.get_sample_size(self.format), self.rate)
        return file
        
    def next_frame(self):
        try:
            next(self.thread)
        except StopIteration:
            self.delete()
            
    def _new_thread(self):
        raise NotImplementedError
 

class Audio_Input(Audio_Device):
       
    defaults = defaults.Audio_Input
    
    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)
        if hasattr(self, "index"):
            self.input_device_index = self.index
        
    def _new_thread(self):
        stream = self.stream
        full_buffer_size = self.full_buffer_size
        while self.active:
            frame_count = stream.get_read_available()
            data = stream.read(frame_count)
            if getattr(self, "data_source", None):
                bytes = frame_count * self.sample_size * self.channels
                data = self.data_source.read(bytes)
            self._data += data
            self.frame_count += frame_count
            if self.frame_count >= self.frames_per_buffer:
                self.data = self._data[:full_buffer_size]
                self._data = self._data[full_buffer_size:]
                self.frame_count -= self.frames_per_buffer
            yield        
            

class Audio_Output(Audio_Device):
            
    defaults = defaults.Audio_Output

    def __init__(self, **kwargs):
        super(Audio_Output, self).__init__(**kwargs)
                
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
            
