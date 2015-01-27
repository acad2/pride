import time
import wave

# install requires python-dev and libasound2:
# sudo apt-get install python-dev
# sudo apt-get install libasound2
# sudo pip install pyalsaaudio
import alsaaudio

import base
import defaults

class Audio_Device(base.Base):

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

    def initialize(self):
        print "%s %s initializing" % (self.name, self.card)
        self.pcm = alsaaudio.PCM(type=self.type, mode=self.mode, card=self.card)
        self.pcm.setchannels(self.channels)
        self.pcm.setrate(self.rate)
        self.pcm.setformat(self.format)
        self.sample_size = self.sample_size
        self.pcm.setperiodsize(self.period_size)

        self.thread = self._new_thread()
        if self.record_to_disk:
            self.file = self._new_wave_file()

    def get_data(self):
        raise NotImplementedError

    def _new_wave_file(self):
        """create a new wave file of appropriate format"""
        filename = ("%s recording.wav" % self.name).replace(" ", "_")
        try:
            file = wave.open(filename, "wb")
        except IOError:
            print "unusable default filename %s" % (self.name)
            file = wave.open("%s.wav" % raw_input("Please enter filename: "), "wb")
        file.setnchannels(self.channels)
        file.setsampwidth(self.format)
        file.setframerate(self.rate)

        return file

    def handle_data(self, audio_data):
        if self.record_to_disk:
            self.file.writeframes(audio_data)

        for client in self.listeners:
            self.send_to(client, audio_data)


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

    def _new_thread(self):
        data = ''
        read_data = self.data_source.read
        period_size = self.period_size
        full_buffer_size = self.full_buffer_size
        silence = "\x00" * period_size
        pcm_write = self.pcm.write

        while True:
            data += read_data(period_size)
            buffer_size = len(data)
            if buffer_size >= full_buffer_size:
                if self.mute:
                    data = silence
                pcm_write(data)
                data = data[buffer_size:]
            yield

    def get_data(self):
        return next(self.thread)
