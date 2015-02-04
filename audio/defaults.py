import mpre.defaults as defaults
Base = defaults.Base
Process = defaults.Process
Thread = defaults.Thread

# audiolibrary

Wav_File = Base.copy()
Wav_File.update({"mode" : "rb",
"filename" : "",
"repeat" : False,
"channels" : 2,
"rate" : 48000,
"sample_width" : 2})

AlsaAudio_Device = Base.copy()
AlsaAudio_Device.update({"channels" : 1,
"rate" : 48000,
"format" : 2, # alsaaudio.PCM_FORMAT_S16_LE
"sample_size" : 16,
"period_size" : 1024,
"card" : "hw:0,0",
"data" : '',
"frame_count" : 0,
"mute" : False})

AlsaAudio_Input = AlsaAudio_Device.copy()
AlsaAudio_Input.update({"type" : 1, # PCM_CAPTURE
"mode" : 1, # PCM_NONBLOCK
"_data" : ''})

AlsaAudio_Output = AlsaAudio_Device.copy()
AlsaAudio_Output.update({"type" : 0, # PCM_PLAYBACK
"mode" : 1}) # PCM_NONBLOCK

PyAudio_Device = Thread.copy()
PyAudio_Device.update({"format" : 8,
"frames_per_buffer" : 1024,
"data" : "",
"record_to_disk" : False,
"frame_count" : 0,
"memory_size" : 65535})

Audio_Input = PyAudio_Device.copy()
Audio_Input.update({"input" : True,
"_data" : ''})

Audio_Output = PyAudio_Device.copy()
Audio_Output.update({"output" : True,
"mute" : False,
"data_source" : None})

Audio_Configuration_Utility = Process.copy()
Audio_Configuration_Utility.update({"config_file_name" : "audiocfg",
"mode" : ("input",),
"auto_start" : False})

Audio_Manager = Process.copy()
Audio_Manager.update({"config_file_name" : 'audiocfg',
"use_defaults" : True,
"priority" : .01})

Audio_Channel = Thread.copy()
Audio_Channel.update({"audio_data" : '',
"memory_size" : 65535})

Audio_Service = Thread.copy()
Audio_Service.update({"memory_size" : 65535})

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