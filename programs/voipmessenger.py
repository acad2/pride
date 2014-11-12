#   mpf.voip_messenger - send and receive text and audio
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

import mmap

import base
import defaults
Event = base.Event

class Voip_Messenger(base.Process):
    
    defaults = defaults.Voip_Messenger
    
    def __init__(self, **kwargs):
        self.log = {}
        self.listeners = []
        self.talking_to = {}
        super(Voip_Messenger, self).__init__(**kwargs)
        self.network_buffer = {}
        self.file = mmap.mmap(-1, 8192 * 2)
        self.keyboard = self.create("keyboard.Keyboard")
        self.audio_service = self.create("audiolibrary.Audio_Service")
        
        file_info = {"format" : self.format,
                     "rate" : self.rate,
                     "channels" : self.channels,
                     "name" : self.name}
        Event("Audio_Manager0", "play_file", file_info, self.file).post()
        options = {"port" : self.port,
                   "incoming" : self._incoming,
                   "outgoing" : self._outgoing}
        self.socket = self.create("networklibrary.UDP_Socket", **options)
        Event("Asynchronous_Network0", "add", self.socket).post()        
        
    def _incoming(self, connection):
        data, _from = connection.recvfrom(self.network_chunk_size)
        self.network_buffer[(connection, _from)] = data
        
    def _outgoing(self, connection, data):
        to, data = data
        connection.sendto(data, to)
        
    def run(self):
        self.audio_service.run()
        self.send_audio()
        try:
            self.handle_input()
        except (AttributeError, ValueError):
            print "Commands: message, call, hangup"
            print "to send a message: message address:port this is the message"
            print "to call: call address:port"
            print "to hangup: hangup address:port"        
        self.handle_incoming()
        
        self.propagate()
        
    def send_audio(self):        
        for channel in self.audio_service.objects["Audio_Channel"]:
            data = channel.read()
            if self.microphone_name in channel.name and data:
                for listener in self.listeners:
                    args = (self.socket, channel.audio_data, listener)                  
                    Event("Asynchronous_Network0", "buffer_data", *args).post()
            channel.audio_data = ''
            
    def handle_input(self):        
        if self.keyboard.input_waiting():
            self.keyboard.get_line(self)
        
        if self.keyboard_input:
            input = self.keyboard_input
            self.keyboard_input = ''
            command, argument = input.split(" ", 1)
            if command == "message":
                address, message = argument.split(' ', 1)
                message = self.message_header + message
            else:
                address = argument
                message = getattr(self, "%s_header" % command)
            ip, port = address.split(":")
            to = (ip, int(port))
            Event("Asynchronous_Network0", "buffer_data", self.socket, message, to).post()

    def handle_incoming(self):
        for _from, data in self.network_buffer.items():
            header, message = data.split(" ", 1)
            if "call" in header:
                if "y" in raw_input("Call from %s; accept? y/n: " % _from).lower():
                    self.calls.apend(_from)
            elif "hangup" in header:
                try:
                    self.calls.remove(_from)
                except ValueError:
                    pass
            elif "audio" in header and _from in self.listening_to:
                self.file.seek(0)
                self.file.write(message)
                self.file.seek(0)
            elif "message" in header:
                try:
                    self.log[_from].write(message + "\n")
                except KeyError:
                    self.log = {_from : open("%s.log" % _from, "a")}
                    self.log[_from].write(message + "\n")            
                print "%s: %s" % (self.talking_to[_from], message)
                
if __name__ == "__main__":
    import vmlibrary
    
    machine = vmlibrary.Machine()
    Event("System0", "create", "audiolibrary.Audio_Manager").post()
    Event("System0", "create", Voip_Messenger).post()
    machine.run()