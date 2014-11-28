#   mpf.defaults - config file - contains attributes:values for new instances
#
#    Copyright (C) 2014  Ella Rose
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

font = time = Surface = NotImplemented
import struct
import socket
from traceback import format_exc
from multiprocessing import cpu_count
from StringIO import StringIO
SCREEN_SIZE = [800, 600]
R, G, B = 180, 180, 180
typeface = 'arial'
NO_ARGS = tuple()
NO_KWARGS = dict()
PROCESSOR_COUNT = 1#cpu_count()

# Base
Base = {"memory_size" : 8192,
"network_chunk_size" : 4096,
"ignore_alerts" : False}

Process = Base.copy()
Process.update({"auto_start" : True, 
"network_buffer" : '',
"keyboard_input" : '',
"priority" : .04,
"minimum_priority" : .04,
"maximum_priority" : .04,
"priority_scales_with" : '',
"update_priority_interval" : 20,
"scale_against" : 1.0,
"scale_operator" : "div"})

Thread = Base.copy()

Hardware_Device = Base.copy()

# vmlibrary

Processor = Hardware_Device.copy()
Processor.update({"ignore_alerts" : True}) # show everything that is processed or not

System = Base.copy()
System.update({"name" : "system",
"status" : "",
"hardware_configuration" : ("vmlibrary.Keyboard", ),
"startup_processes" : (("networklibrary.Asynchronous_Network", NO_ARGS, NO_KWARGS), )})

Machine = Base.copy()
Machine.update({"processor_count" : PROCESSOR_COUNT,
"hardware_configuration" : (("vmlibrary.Keyboard", NO_ARGS, NO_KWARGS), ),
"system_configuration" : (("vmlibrary.System", NO_ARGS, NO_KWARGS), )})

# inputlibrary
Keyboard = Hardware_Device.copy()

# voipmessenger
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

# stdout display
Stdout_Display = Process.copy()
Stdout_Display.update({"height" : 600,
"width" : 840,
"components" : ("stdoutdisplay.Border",)})

Border = Base.copy()
Border.update({"height" : 600,
"width" : 840,
"character" : '#'})

Task_Scheduler = Process.copy()

Application = Process.copy()
Application.update({"font" : (typeface, 16), 
"pack_mode" : "layer"})

Messenger = Application.copy()

Explorer = Application.copy()
Explorer.update({"time" : ""})

# interpreter
Shell = Process.copy()
Shell.update({"username" : "root", 
"password" : "password", 
"prompt" : ">>> ", 
"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.', 
"definition" : False, 
"traceback" : format_exc, 
"backup_write" : '', 
"login_stage" : '', 
"auto_start" : False,
"auto_login" : True,
"host_name" : "localhost",
"port" : 40000,
"startup_definitions" : ''}) 

Shell_Service = Process.copy()
Shell_Service.update({"interface" : "0.0.0.0", 
"port" : 40000, 
"prompt" : ">>> ", 
"copyright" : 'Type "help", "copyright", "credits" or "license" for more information.', 
"definition" : False, 
"traceback" : format_exc, 
"backup_write" : ''}) 

# audiolibrary

Wav_File = Base.copy()
Wav_File.update({"mode" : "rb",
"filename" : "",
"repeat" : False})

AlsaAudio_Device = Base.copy()
AlsaAudio_Device.update({"channels" : 1,
"rate" : 48000,
"format" : 2, # alsaaudio.PCM_FORMAT_S16_LE
"sample_size" : 16,
"period_size" : 1024,
"record_to_disk" : False,
"card" : "hw:0,0",
"data" : '',
"frame_count" : 0})

AlsaAudio_Input = AlsaAudio_Device.copy()
AlsaAudio_Input.update({"type" : 1, # PCM_CAPTURE
"mode" : 1, # PCM_NONBLOCK
"_data" : ''}) 

AlsaAudio_Output = AlsaAudio_Device.copy()
AlsaAudio_Output.update({"type" : 0, # PCM_PLAYBACK
"mode" : 1}) # PCM_NONBLOCK

PyAudio_Device = Base.copy()
PyAudio_Device.update({"format" : 8,
"frames_per_buffer" : 768,
"data" : "",
"record_to_disk" : False,
"frame_count" : 0})

Audio_Input = PyAudio_Device.copy()
Audio_Input.update({"input" : True,
"_data" : ''})

Audio_Output = PyAudio_Device.copy()
Audio_Output.update({"output" : True, 
"mute" : False,
"data_source" : StringIO()})

Audio_Configuration_Utility = Process.copy()
Audio_Configuration_Utility.update({"config_file_name" : "audiocfg",
"mode" : ("input",),
"auto_start" : False})

Audio_Manager = Process.copy()
Audio_Manager.update({"config_file_name" : 'audiocfg',
"use_defaults" : True,
"priority" : .005})

Audio_Channel = Thread.copy()
Audio_Channel.update({"audio_data" : '',
"memory_size" : 65535})

Audio_Service = Thread.copy()
Audio_Service.update({"memory_size" : 65535})

# networklibrary
Connection = Base.copy()
Connection.update({"socket_family" : socket.AF_INET, 
"socket_type" : socket.SOCK_STREAM})

Server = Connection.copy()
Server.update({"interface" : "localhost", 
"port" : 0, 
"backlog" : 50,
"name" : "", 
"reuse_port" : 0,
"inbound_connection_type" : "networklibrary.Inbound_Connection"})
   
Outbound_Connection = Connection.copy()
Outbound_Connection.update({"ip" : "localhost",
"port" : 80,
"target" : None,
"as_port" : 0,
"timeout" : 10,
"timeout_notify" : True})
   
Inbound_Connection = Connection.copy()

Download = Outbound_Connection.copy()
Download.update({"filesize" : 0,
"filename" : None,
"filename_prefix" : "Download",
"download_in_progress" : False,
"network_chunk_size" : 16384,
"port" : 40021})

Upload = Inbound_Connection.copy()
Upload.update({"use_mmap" : False,
"network_chunk_size" : 16384,
"file" : '',
"mmap_file" : False})

UDP_Socket = Base.copy()
UDP_Socket.update({"interface" : "0.0.0.0",
"port" : 0,
"timeout" : 10})

# only addresses in the range of 224.0.0.0 to 230.255.255.255 are valid for IP multicast
Multicast_Beacon = Base.copy()
Multicast_Beacon.update({"packet_ttl" : struct.pack("b", 127),
"multicast_group" : "224.0.0.0", 
"multicast_port" : 1929})

Multicast_Receiver = Base.copy()
Multicast_Receiver.update({"listener_address" : "0.0.0.0",
"multicast_group" : "224.0.0.0",
"port" : 0})

Basic_Authentication_Client = Thread.copy()

Basic_Authentication = Thread.copy()

Asynchronous_Network = Process.copy()
Asynchronous_Network.update({"number_of_sockets" : 0,
"priority_scales_with" : "number_of_sockets",
"update_priority_interval" : 5})

Service_Listing = Process.copy()

# File Manager
File_Server = Process.copy()
File_Server.update({"interface" : "0.0.0.0",
"port" : 40021,
"network_chunk_size" : 16384,
"asynchronous_server" : True})

# Guilibrary
Display = Process.copy()
Display.update({"x" : 0, 
'y' : 0, 
"size" : SCREEN_SIZE, 
"layer" : 0, 
"max_layer" : 0, 
"drawing" : False})

# Widgets
# these are the required attributes for a fully draw-able object
Gui_Object = Base.copy()
Gui_Object.update({'x' : 0, 
        'y' : 0, 
        'size' : SCREEN_SIZE, 
        "layer" : 1, 
        "color" : (R, G, B), 
        "outline" : 5, 
        "popup" : False, 
        "pack_mode" : '', 
        "typeface" : (typeface, 16), 
        "pack_modifier" : '', 
        "color_scalar" : .6})

Window = Gui_Object.copy()
Window.update({"title_bar" : False, 
"pack_mode" : "layer"})

Container = Window.copy()
Container.update({"alpha" : 1, 
        "pack_mode" : "vertical"})

Button = Container.copy()
Button.update({"shape" : "rect"})

Popup_Window = Window.copy()
Popup_Window.update({"popup" : True, 
        "pack_modifier" : lambda parent, child: setattr(child, "position", (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))})

File_Menu = Popup_Window.copy()
File_Menu.update({"pack_mode" : "vertical", 
        "pack_modifier" : lambda parent, child: setattr(child, "y", child.y+parent.size[1])})

Right_Click_Menu = Popup_Window.copy()
Right_Click_Menu.update({"pack_mode": "layer", 
"size" : (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)})

Homescreen = Window.copy()
Homescreen.update({"background_filename" : "C:\\test.jpg"})

Property_Editor = Window.copy()
Property_Editor.update({"pack_modifier" : lambda parent, child:\
setattr(child, "position", (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))})

Menu_Bar = Container.copy()
Menu_Bar.update({"pack_mode" : "menu_bar"})

Title_Bar = Menu_Bar.copy()
Title_Bar.update({"pack_modifier" : lambda parent, child:\
setattr(child, "y", child.y+child.size[1])})

Task_Bar = Menu_Bar.copy()
Task_Bar.update({"pack_modifier" : lambda parent, child:\
setattr(child, "y", (parent.y+parent.size[1])-child.size[1])\
}) # ^ aligns the bottom left corners of the parent and child object

Date_Time = Button.copy()
Date_Time.update({"pack_mode" : "horizontal"})

Help_Bar = Button.copy()
Help_Bar.update({"pack_mode" : "horizontal"})

Property_Button = Button.copy()
Property_Button.update({"property" : '', 
"display" : False})

File_Button = Button.copy()
File_Button.update({"display" : False})

Text_Line = Button.copy()
Text_Line.update({"edit_mode" : False})

Text_Character = Button.copy()
Text_Character.update({"text" : "", 
        "pack_mode" : "text", 
        "outline" : 0})
