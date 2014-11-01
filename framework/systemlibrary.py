#   mpf.systemlibrary - systems for running on a vm
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

import sys
import traceback
import time
exit, modules = sys.exit, sys.modules
from operator import attrgetter, itemgetter
from weakref import proxy


import base
import defaults
Event = base.Event


class System(base.Base):
    """a class for managing components and applications.
    
    usually holds components such as the event handler, network manager, display,
    and so on. hotkeys set at the system level will be called if the key(s) are
    pressed and no other active object have the keypress defined."""
    
    defaults = defaults.System
    #hotkeys are specified in the form of keycode:Event pairs in a dictionary.
    hotkeys = {}
        
    def __init__(self, **kwargs):
        # used to explore the system via the console
        globals()["system_reference"] = self
        
        # sets default attributes
        super(System, self).__init__(**kwargs)
        
        # enable the event handler to reference the system the same way as everyone else
        self.objects["System"] = [self]
        #v: print self.startup_processes
        for component, args, kwargs in self.startup_processes:
            #v: print "creating", component, args, kwargs
            self.create(component, *args, **kwargs)           
                    
    def exit(self):
        Event("Machine", "delete", self).post()
     
    def run(self):
        pass    
                
        
class Application(base.Process):
    """a base application object to subclass from.
    
    defunct: used for graphical applications from pygame days"""
    defaults = defaults.Application
    # subclass from me and set some hotkeys!
    
    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)
            
                
class Messenger(base.Process):

    defaults = defaults.Messenger
    
    def __init__(self, **kwargs):
        super(Messenger, self).__init__(**kwargs)
        self.conversations = {}
                       
        Event("Asynchronous_Network0", "create", "networklibrary.Server", incoming=self._receive_message,\
        outgoing=self._send_message, on_connection=self.register_connection, port=41337, name="Messenger").post()
        
    def _receive_message(self, sock):
        data = sock.recv(1024)
        if not data:
            print "%s disconnected" % sock.getpeername()
            sock.close()
            sock.delete()
        print "%s: %s" % (sock.getpeername(), data)
        Event("Asynchronous_Network0", "buffer_data", sock, data).post()
        
    def _send_message(self, sock, data):
        sock.send(data)
                
    def run(self):
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Messenger0", "run").post()
        else:
            Event("Asynchronous_Network0", "delete_server", "Messenger").post()
            
    def register_connection(self, connection, address):
        print "You may now speak with %s via %s.send..." % (address, self)
        self.conversations[address] = connection
    
    def send(self, message):
        destination, text = "".join(message).split("<")
        ip, port = destination.split(":")
        port = int(port)
        connection = self.conversations[(str(ip), port)]
        print "sending", text, "to", destination
        Event("Asynchronous_Network0", "buffer_data", connection, text).post()
  
    
class Explorer(Application):
    """defunct graphical application from pygame days. Will be reworked
    when graphical applications are worked back in"""
    defaults = defaults.Explorer
    
    def __init__(self, **kwargs):
        super(Explorer, self).__init__(**kwargs)
        self.homescreen = proxy(self.create("widgetlibrary.Homescreen"))
        self.time_service()
        Event("Organizer0", "pack", self).post()
        Event("Display0", "draw", self).post()
                
    def run(self):        
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Explorer0", "run").post()
                           
    def _draw(self):
        return self.homescreen._draw()   