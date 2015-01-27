# pyaudio requires: libportaudio0, libportaudio2, libportaudiocpp0, and portaudio19-dev on linux
# linux installation instructions:
# if installation was already attempted, do: sudo apt-get remove python-pyaudio
# wget http://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_i386.deb
# sudo dpkg -i python-pyaudio_0.2.8-1_i386.deb
import wave
import sys
from contextlib import contextmanager
from ctypes import *
import pyaudio

import base
from utilities import Latency
import defaults
Instruction = base.Instruction

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
        self.listeners = []
        self.sample_size = PORTAUDIO.get_sample_size(pyaudio.paInt16)
        super(Audio_Device, self).__init__(**kwargs)

    def initialize(self):
        self.alert("initializing device {0} with options: {1}",
                  (self.name, self.options), "vv")
        try:
            self.stream = PORTAUDIO.open(**self.options)
        except:
            raise

        self.thread = self._new_thread()

        if self.record_to_disk:
            self.file = self._new_wave_file()

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

    def get_data(self):
        raise NotImplementedError

    def handle_data(self, audio_data):
        if self.record_to_disk:
            self.file.writeframes(audio_data)

        for client in self.listeners:
            self.send_to(client, audio_data)


class Audio_Input(Audio_Device):

    defaults = defaults.Audio_Input

    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)
        self.thread = self._new_thread()
        if hasattr(self, "index"):
            self.input_device_index = self.index

    def _new_thread(self):
        stream = self.stream
        get_read_available = stream.get_read_available
        read_stream = stream.read

        data_source = getattr(self, "data_source", None)
        data_read = getattr(data_source, "read", None)
        handle_data = self.handle_data

        byte_scalar = self.sample_size * self.channels
        frames_per_buffer = self.frames_per_buffer
        full_buffer_size = self.full_buffer_size
        frame_counter = self.frame_count
        _data = ''

        while True:
            frame_count = get_read_available()
            if data_source:
                byte_range = frame_count * byte_scalar
                data = data_read(byte_range)
            else:
                data = read_stream(frame_count)
            _data += data
            frame_counter += frame_count

            if frame_counter >= frames_per_buffer:
                frame_counter -= frames_per_buffer
                handle_data(_data[:full_buffer_size])
                _data = data[full_buffer_size:]
            yield

    def get_data(self):
        return next(self.thread)


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
        stream_write = stream.write
        get_write_available = stream.get_write_available

        frames_per_buffer = self.frames_per_buffer
        silence = "\x00" * frames_per_buffer

        read_data = self.data_source.read
        handle_data = self.handle_data

        while True:
            number_of_frames = get_write_available()
            if number_of_frames >= frames_per_buffer:
                data = read_data(frames_per_buffer)
                handle_data(data)
                if self.mute:
                    data = silence
                stream_write(data)
            yield

    def get_data(self):
        return next(self.thread)
