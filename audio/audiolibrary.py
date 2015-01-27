import array
import pickle
import struct
import wave
import sys

if "linux" in sys.platform:
    import alsaaudiodevices as audio_devices
    alsaaudio = audio_devices.alsaaudio
else:
    import portaudiodevices as audio_devices
    pyaudio = audio_devices.pyaudio
    PORTAUDIO = audio_devices.PORTAUDIO

import base
import vmlibrary
import defaults
from utilities import Latency
Instruction = base.Instruction

Audio_Device = audio_devices.Audio_Device
Audio_Input = audio_devices.Audio_Input
Audio_Output = audio_devices.Audio_Output

class Wav_File(base.Base):

    defaults = defaults.Wav_File

    def __init__(self, **kwargs):
        super(Wav_File, self).__init__(**kwargs)
        _file = self.file = wave.open(self.filename, self.mode)
        if 'r' in self.mode:
            channels, sample_width, rate, number_of_frames, comptype, compname = self.file.getparams()
            self.channels = channels
            self.sample_width = sample_width
            self.format = 2 # hardcoded to PCM_FORMAT_S16_LE for quick fix
            self.rate = rate
            self.number_of_frames = number_of_frames
            self.comptype = comptype
            self.compname = compname
        else:
            _file.setnchannels(self.channels)
            _file.setsampwidth(self.sample_width)
            _file.setframerate(self.rate)
            #self.file.setparams((self.channels, self.sample_width, self.rate, 0, None, ''))
            format_args = (self.channels, self.sample_width, self.rate)
        message = "opened wav file with channels: {0}, format: {1}, rate: {2}"
        self.alert(message, (self.channels, self.sample_width, self.rate), level="vv")

    def read(self, size):
        data = self.file.readframes(size)
        if self.repeat and (self.file.tell() == self.number_of_frames):
            self.file.rewind()
        return data

    def tell(self):
        return self.file.tell()

    def write(self, data):
        self.file.writeframes(data)

    def close(self):
        self.file.close()


class Audio_Configuration_Utility(vmlibrary.Process):

    defaults = defaults.Audio_Configuration_Utility

    def __init__(self, **kwargs):
        self.selected_devices = []
        super(Audio_Configuration_Utility, self).__init__(**kwargs)

        if "default" in self.mode:
            default_input, default_output = self.get_default_devices()
            self.selected_devices.append(default_input)
            self.selected_devices.append(default_output)
            self.write_config_file(self.selected_devices)
            self.delete()
        else:
            self.all_devices = self.get_all_devices()
            instruction = Instruction("Audio_Configuration_Utility", "run")
            instruction.component = self
            instruction.execute()

    def write_config_file(self, device_list):
        with open(self.config_file_name, "wb") as config_file:
            for device in device_list:
                print device
            pickle.dump(device_list, config_file)
            config_file.flush()
            config_file.close()

    def get_all_devices(self):
        if "linux" in sys.platform:
            devices = dict((index, {"card" : "hw:{0},0".format(index), "name" : device_name}) for index, device_name in enumerate(alsaaudio.cards()))
        else:
            devices = {}
            for device_number in xrange(PORTAUDIO.get_device_count()):
                device_info = PORTAUDIO.get_device_info_by_index(device_number)
                options = {"channels" : max(device_info["maxOutputChannels"], device_info["maxInputChannels"]),
                         "rate" : int(device_info["defaultSampleRate"]),
                         "name" : device_info["name"],
                         "index" : device_info["index"]}
                devices[device_number] = options
        return devices

    def print_display_devices(self, device_dict):
        for key, value in device_dict.items():
            print "%s: %s" % (key, value)

    def get_selections(self):
        selection = ""
        self.selected_devices = []

        while "done" not in selection:
            print "\n"*80
            print "type 'done' to finish selecting..."
            print "**************************************"
            self.print_display_devices(self.all_devices)
            print "currently using: ", [str(item) for item in self.selected_devices]
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
                    name = raw_input("Rename device or press enter for default name: ")
                    if name:
                        device["name"] = name
                    self.selected_devices.append(device)
        print "finished selecting devices"

    @staticmethod
    def get_default_devices():
        if "linux" in sys.platform:
            input, output = "hw:0,0", "hw:0,0"
        else:
            host_api_info = PORTAUDIO.get_default_host_api_info()
            input_index = host_api_info["defaultInputDevice"]
            output_index = host_api_info["defaultOutputDevice"]
            input = PORTAUDIO.get_device_info_by_index(input_index)
            output = PORTAUDIO.get_device_info_by_index(output_index)
        return input, output

    def run(self):
        self.get_selections()
        self.write_config_file(self.selected_devices)
        self.delete()
        if getattr(self, "exit_when_finished", None):
            exit()


class Audio_Manager(vmlibrary.Process):

    defaults = defaults.Audio_Manager

    def _get_devices(self):
        return self.objects.get("Audio_Input", []) + self.objects.get("Audio_Output", [])

    audio_devices = property(_get_devices)

    def __init__(self, **kwargs):
        device_names = self.device_names = {}
        self.latency = Latency(name="audio_manager")
        super(Audio_Manager, self).__init__(**kwargs)
        if self.config_file_name:
            try:
                self.load_config_file()
            except:
                raw_input("Please run audio_config_utility. No config file found")
                Instruction("System", "exit").execute()
        elif self.use_defaults:
            input_info, output_info = Audio_Configuration_Utility.get_default_devices()
            
            input = self.create(Audio_Input, input_info)
            output = self.create(Audio_Output, output_info)
            
            device_names[input.instance_name] = input
            device_names[output.instance_name] = output
            
            input.initialize()
            output.initialize()

    def load_config_file(self):
        with open(self.config_file_name, "rb") as config_file:
            for device_info in pickle.load(config_file):
                device = self.create(Audio_Input, **device_info)
                self.device_names[device.instance_name] = device
                device.initialize()

    def send_channel_info(self, listener):
        """usage: Instruction("Audio_Manager", "send_channel_info", my_object).execute()
        => Message: "Device_Info;;" + pickled list containing dictionaries

        Request a listing of available audio channels to the specified instances
        memory. This message can be retrieved via instance.read_messages()"""
        channel_info = []
        for device in self.audio_devices:
            options = dict(**device.options)
            options["name"] = device.name
            options["device_name"] = device.instance_name
            options["sample_size"] = device.sample_size
            channel_info.append(options)
        channel_list = pickle.dumps(channel_info)
        self.send_to(listener.instance_name, "Channel_Info;;" + channel_list)

    def add_listener(self, listener, device_name):
        return self.device_names[device_name].listeners.append(listener.instance_name)

    def run(self):
        #self.latency.update()
        #self.latency.display()
        for device in self.audio_devices:
            device.get_data()
        self.run_instruction.execute()

    def play_file(self, file_info, file, to=None, mute=False, record=False):
        _format = file_info["format"] # in bytes, pyaudio needs it's own constant instead
        try:
            format_name = PORTAUDIO.format_mapping[_format]
            constant = getattr(pyaudio, format_name)
            _format = constant
            sample_size = int(format_name[-2:])
        except NameError:
            pass
        options = {"data_source" : file,
                   "mute" : mute,
                   "format" : _format,
                   "rate" : file_info["rate"],
                   "channels" : file_info["channels"],
                   "name" : file_info["name"]}
        speaker = self.create(Audio_Output, **options)
        speaker.initialize()

        if to:
            speaker.listeners.append(to.instance_name)

    def record(self, device_name):
        device = self.device_names[device_name]
        device.file = device._new_wave_file()
        device.record_to_disk = True


class Audio_Channel(vmlibrary.Thread):

    defaults = defaults.Audio_Channel

    def __init__(self, **kwargs):
        super(Audio_Channel, self).__init__(**kwargs)
        self.frame = self._new_thread()

    def run(self):
        return next(self.frame)

    def _new_thread(self):
        read_messages = self.read_messages
        join = ''.join
        while True:
            messages = read_messages()
            if messages:
                self.audio_data = join(messages)
            yield

    def read(self, bytes=0):
        if not bytes:
            bytes = len(self.audio_data)
        data = self.audio_data[:bytes]
        self.audio_data[bytes:]
        return data


class Audio_Service(vmlibrary.Thread):

    defaults = defaults.Audio_Service

    def _get_channels(self):
        return self.objects["Audio_Channel"]
    channels = property(_get_channels)

    def __init__(self, **kwargs):
        self.channel_configuration = {}
        self.audio_data = {}
        self.clients_listening_to = {}
        self.input_channels = {}
        super(Audio_Service, self).__init__(**kwargs)
        self.network_buffer = {}
        self.objects["Audio_Channel"] = []
        self.frame = self._new_thread()
        Instruction("Audio_Manager", "send_channel_info", self).execute()

    def run(self):
        return next(self.frame)

    def _new_thread(self):
        messages = None
        channels = self.objects["Audio_Channel"]

        while not messages:
            messages = self.read_messages()
            yield

        for message in messages:
            header, message = message.split(";;")
            channel_configuration = pickle.loads(message)
            for channel_info in channel_configuration:
                name = channel_info["name"]
                device_name = channel_info["device_name"]
                channel_info["latency"] = Latency(name=name)
                channel = self.create(Audio_Channel, **channel_info)
                Instruction("Audio_Manager", "add_listener", channel, device_name).execute()
        yield

        while True:
            for channel in channels:
                channel.run()
            yield
