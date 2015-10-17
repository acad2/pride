import time
import wave
import contextlib

import pride
import pride.base as base
import pride.audio.audiolibrary as audiolibrary
objects = pride.objects

# to install alsaaudio, use pride.audio.utilities.install_pyalsaaudio
import alsaaudio

class Audio_Device(audiolibrary.Audio_Reactor):

    possible_options = ("rate", "channels", "format", "sample_size", 
                        "period", "type", "card")
                        
    def _get_options(self):
        return dict((attribute, getattr(self, attribute)) for attribute in
                     self.possible_options if 
                     getattr(self, attribute, None) is not None)
    options = property(_get_options)

    def _get_full_buffer_size(self):
        return self.channels * self.period_size * (self.sample_size / 8)
    full_buffer_size = property(_get_full_buffer_size)

    defaults = {"channels" : 1,
                "rate" : 48000,
                "format" : 2, # alsaaudio.PCM_FORMAT_S16_LE
                "sample_size" : 16,
                "period_size" : 1024,
                "card" : "hw:0,0",
                "data" : '',
                "data_source" : None,
                "frame_count" : 0,
                "mute" : False}

    def __init__(self, **kwargs):
        super(Audio_Device, self).__init__(**kwargs)
        self.alert("{} {} initializing",
                  (self.name, self.card),
                  level='v')
                  
        self.pcm = alsaaudio.PCM(type=self.type, mode=self.mode, card=self.card)
        self.pcm.setchannels(self.channels)
        self.pcm.setrate(self.rate)
        self.pcm.setformat(self.format)
        self.pcm.setperiodsize(self.period_size)

    def get_data(self):
        raise NotImplementedError

    def mute(self):
        if self.is_muted:
            self.data_source = '\x00' * self.full_buffer_size
            self.is_muted = True
        else:
            self.is_muted = False


class Audio_Input(Audio_Device):

    defaults = {"type" : 1, # PCM_CAPTURE
                "mode" : 1, # PCM_NONBLOCK
                "_data" : ''}

    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)
        if not self.data_source:
            self.data_source = self.pcm            
        self.byte_scalar = self.sample_size / 8
    
    @contextlib.contextmanager
    def listeners_preserved(self):
        old_listeners = self.listeners
        try:
            yield
        finally:
            self.listeners = old_listeners 
            
    def get_data(self):
        frame_count, data = self.pcm.read()
        self.handle_audio_output(data)
        
        if self.playing_files:
            byte_count = frame_count * self.byte_scalar
            for _file in self.playing_files:
                file_data = _file.read(byte_count)
                for listener in self.playing_to[_file]:
                    objects[listener].handle_audio_input(_file.name, file_data)
                                                 
    def play_file(self, _file, listeners=("Audio_Output", )):
        self.playing_files.append(_file)
        self.playing_to[_file] = listeners
        for listener in listeners:
            objects[listener].set_input_device(self.instance_name)

    def stop_file(self, _file):
        self.playing_files.remove(_file)
        
        for listener in self.playing_to[_file]:
            objects[listener].handle_end_of_stream()
        del self.playing_to[_file]
        
        
class Audio_Output(Audio_Device):

    defaults = {"type" : 0, # PCM_PLAYBACK
                "mode" : 1} # PCM_NONBLOCK

    def __init__(self, **kwargs):
        super(Audio_Output, self).__init__(**kwargs)

    def handle_audio_input(self, sender, audio_data):
        if self.listeners:
            super(Audio_Output, self).handle_audio_input(sender, audio_data)
        self.pcm.write(audio_data)
                
    """def _new_thread(self):
        data_source = getattr(self, "data_source", self.pcm)
        read_data = self.data_source.read
        period_size = self.period_size
        full_buffer_size = self.full_buffer_size
        silence = "\x00" * period_size
        pcm_write = self.pcm.write

        if self.input_from == self.data_source.read:
            read_data = partial(self.data_source.read, full_buffer_size)
        else:
            read_data = lambda: ''.join(self.read_messages())
        
        data = ''
        while True:
            data += read_data()            
            buffer_size = len(data)
            if buffer_size >= full_buffer_size:
                if self.mute:
                    data = silence
                pcm_write(data[:full_buffer_size])
                data = data[full_buffer_size:]
            yield

    def get_data(self):
        return next(self.thread)"""
