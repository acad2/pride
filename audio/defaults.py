
Base = defaults.Base
Process = defaults.Process
Reactor = defaults.Reactor

# audiolibrary

Audio_Reactor = Reactor.copy()
Audio_Reactor.update({"source_name" : ''})

Wav_File = Audio_Reactor.copy()
Wav_File.update({"mode" : "rb",
"filename" : "",
"repeat" : False,
"channels" : 2,
"rate" : 48000,
"sample_width" : 2})

AlsaAudio_Device = Audio_Reactor.copy()
AlsaAudio_Device.update({"channels" : 1,
"rate" : 48000,
"format" : 2, # alsaaudio.PCM_FORMAT_S16_LE
"sample_size" : 16,
"period_size" : 1024,
"card" : "hw:0,0",
"data" : '',
"data_source" : None,
"frame_count" : 0,
"mute" : False})

AlsaAudio_Input = AlsaAudio_Device.copy()
AlsaAudio_Input.update({"type" : 1, # PCM_CAPTURE
"mode" : 1, # PCM_NONBLOCK
"_data" : ''})

AlsaAudio_Output = AlsaAudio_Device.copy()
AlsaAudio_Output.update({"type" : 0, # PCM_PLAYBACK
"mode" : 1}) # PCM_NONBLOCK

PyAudio_Device = Reactor.copy()
PyAudio_Device.update({"format" : 8,
"frames_per_buffer" : 1024,
"data" : "",
"record_to_disk" : False,
"frame_count" : 0,
"source_name" : '',
"data_source" : '',
"mute" : False,
"silence" : b"\x00" * 65535})

Audio_Input = PyAudio_Device.copy()
Audio_Input.update({"input" : True,
"data" : '',
"priority" : .01})

Audio_Output = PyAudio_Device.copy()
Audio_Output.update({"output" : True})

Config_Utility = Process.copy()
Config_Utility.update({"config_file_name" : "audiocfg",
"mode" : ("input",),
"auto_start" : False})

Audio_Manager = Reactor.copy()
Audio_Manager.update({"config_file_name" : '',
"use_defaults" : True,
"configure" : False})

Voip_Messenger = Process.copy()
Voip_Messenger.update({"microphone_name" : "microphone",
"port" : 40100,
"name" : "voip_messenger",
"channels" : 2,
"rate" : 48000,
"format" : 2,
"message_header" : "message",
"call_header" : "call",
"hangup_header" : "hangup",
"audio_header" : "audio"})