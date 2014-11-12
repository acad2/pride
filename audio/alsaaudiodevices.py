import alsaaudio
import wave

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
    
    def _new_thread(self):
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
	print "setting sample width to", self.sample_size
        file.setsampwidth(self.format)
        file.setframerate(self.rate)
        print "created wave file: channels %s, sample width %s, rate %s" % (self.channels, self.format, self.rate)
        return file
         
         
class Audio_Input(Audio_Device):
    
    defaults = defaults.AlsaAudio_Input
    
    def __init__(self, **kwargs):
    	super(Audio_Input, self).__init__(**kwargs)
	self.thread = self._new_thread()

    def _new_thread(self):
        full_buffer_size = self.full_buffer_size
        while True:
            frame_count, data = self.pcm.read()
            if getattr(self, "data_source", None):
                bytes = frame_count * (self.sample_size / 8)
                data = self.data_source.read(bytes)
            self._data += data
            self.frame_count += frame_count
            if self.frame_count >= self.period_size:
                self.data = self._data[:full_buffer_size]
                self._data = self._data[full_buffer_size:]
                #print "got %s/%s bytes of audio data" % (len(self.data), full_buffer_size), time.time()
                self.frame_count -= self.period_size
            yield
            
    def next_frame(self):
        next(self.thread)
        

class Audio_Output(Audio_Device):
                
    defaults = defaults.AlsaAudio_Output
    
    def __init__(self, **kwargs):
        super(Audio_Output, self).__init__(**kwargs)
        self.thread = self._new_thread()

    def _new_thread(self):
        full_buffer_size = self.full_buffer_size
        while True:
            self.data += self.data_source.read(self.period_size)
            buffer_size = len(self.data)
            if buffer_size >= full_buffer_size:
                data = self.data
                if self.mute:
                    data = "\x00" * self.period_size
                self.pcm.write(data)
                self.data = self.data[buffer_size:]
            yield
            
    def next_frame(self):
        next(self.thread)
