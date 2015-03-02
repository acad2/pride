import time
import wave

# install requires python-dev and libasound2:
# sudo apt-get install python-dev
# sudo apt-get install libasound2
# sudo pip install pyalsaaudio
import alsaaudio

import mpre.base as base
import defaults

class Audio_Device(base.Reactor):

    possible_options = ("rate", "channels", "format", "sample_size", "period", "type", "card")
    def _get_options(self):
        options = {}
        for option in self.possible_options:
            value = getattr(self, option, None)
            if value:
                options[option] = value
        return options
    options = property(_get_options)

    def _get_full_buffer_size(self):
        return self.channels * self.period_size * (self.sample_size / 8)
    full_buffer_size = property(_get_full_buffer_size)

    defaults = defaults.AlsaAudio_Device

    def __init__(self, **kwargs):
        self.listeners = []
        super(Audio_Device, self).__init__(**kwargs)
        print "%s %s initializing" % (self.name, self.card)
        self.pcm = alsaaudio.PCM(type=self.type, mode=self.mode, card=self.card)
        self.pcm.setchannels(self.channels)
        self.pcm.setrate(self.rate)
        self.pcm.setformat(self.format)
        self.sample_size = self.sample_size
        self.pcm.setperiodsize(self.period_size)

        self.thread = self._new_thread()

    def get_data(self):
        raise NotImplementedError

    def handle_data(self, audio_data):
        for client in self.listeners:
            self.reaction(client, audio_data)


class Audio_Input(Audio_Device):

    defaults = defaults.AlsaAudio_Input

    def __init__(self, **kwargs):
        super(Audio_Input, self).__init__(**kwargs)

    def get_data(self):
        return next(self.thread)

    def _new_thread(self):
        pcm_read = self.pcm.read
        data_source = getattr(self, "data_source", None)
        read_data = getattr(data_source, "read", None)
        
        byte_scalar = self.sample_size / 8
        handle_data = self.handle_data

        while True:
            frame_count, data = pcm_read()
            if data_source:
                byte_range = frame_count * byte_scalar
                data = read_data(byte_range)
            yield handle_data(data)


class Audio_Output(Audio_Device):

    defaults = defaults.AlsaAudio_Output

    def __init__(self, **kwargs):
        super(Audio_Output, self).__init__(**kwargs)
        if not self.data_source:
            self.mute = True
        else:
            try:
                self.data_source.listeners.append(self.instance_name)
            except AttributeError:
                self.input_from = self.data_source.read
                
    def _new_thread(self):
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
        return next(self.thread)
