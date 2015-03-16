import time
import wave

# install requires python-dev and libasound2:
# sudo apt-get install python-dev
# sudo apt-get install libasound2
# sudo pip install pyalsaaudio
import alsaaudio

import mpre.base as base
import mpre.audio.audiolibrary as audiolibrary
import mpre.audio.defaults as defaults

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

    defaults = defaults.AlsaAudio_Device

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

    defaults = defaults.AlsaAudio_Input

    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)
        if not self.data_source:
            self.data_source = self.pcm
            
        self.byte_scalar = self.sample_size / 8
        
    def get_data(self):
        frame_count, data = pcm_read()
        if self.data_source is not self.pcm:
            data = self.data_source.read(frame_count * self.byte_scalar)
        self.handle_audio_output(data)
        

class Audio_Output(Audio_Device):

    defaults = defaults.AlsaAudio_Output

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
