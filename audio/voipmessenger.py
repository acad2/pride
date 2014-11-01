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

import pickle
import mmap

import base
import defaults

class Voip_Messenger(base.Process):
    
    defaults = defaults.Voip_Messenger
    
    def __init__(self, *args, **kwargs):
        self.log = {}
        self.talking_to = {}
        super(Voip_Messenger, self).__init__(*args, **kwargs)
        self.file = mmap.mmap(-1, 8192 * 2)
        self.keyboard = self.create("keyboard.Keyboard")
        Event("Audio_Manager0", "add_listener", self, self.microphone_name).post()
        Event("Audio_Manager0", "play_file", self.file).post()
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
        if self.keyboard.input_waiting():
            to, message = self.keyboard.get_line().split(":", 1)
            Event("Network_Manager", "buffer_data", self.sock, message, to).post()
            
        for message in self.get_messages:
            header, data = message.split(";;", 1)
            if self.microphone_name in header: # microphone input
                for listener in self.listeners:
                    Event("Asynchronous_Network0", "buffer_data", self.socket, data, listener).post()
  
        for _from, data in self.network_buffer.items():
            sent_to, message = data.split(":", 1)
            if "audio" in message:
                self.file.seek(0)
                self.file.write(message)
                self.file.seek(0)
            else:
                try:
                    self.log[_from].write(data+"\n")
                except KeyError:
                    self.log = {_from : open("%s.log" % _from, "a")}
                    self.log[_from].write(data+"\n")            
                print "%s: %s" % (self.talking_to[_from], message)
                
if __name__ == "__main__":
    import machinelibrary
    machine = machinelibrary.Machine()
    Event("System0", "create", "Voip_Messenger").post()