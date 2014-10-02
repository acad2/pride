# standard modules
import sys
import traceback
import time
exit, modules = sys.exit, sys.modules
from operator import attrgetter, itemgetter
from socket import gethostname
from weakref import proxy
from codeop import CommandCompiler

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
        
    def __init__(self, *args, **kwargs):
        # used to explore the system via the console
        globals()["system_reference"] = self
        
        # sets default attributes
        super(System, self).__init__(*args, **kwargs)
        
        # enable the event handler to reference the system the same way as everyone else
        self.objects["System"] = [self]
        print self.startup_processes
        for component, args, kwargs in self.startup_processes:
            #v: print "creating", component, args, kwargs
            self.create(component, *args, **kwargs)           
                    
    def exit(self):
        Event("Machine", "delete", self).post()
     
    def run(self):
        pass    
        
        
class Idle(base.Process):
    """the system idle process. can be used to do maintainence during downtime"""
    defaults = defaults.Idle
    
    def __init__(self, *args, **kwargs):
        super(Idle, self).__init__(*args, **kwargs)
        self.before_sleep = self.after_sleep = []
        
    def run(self):
        for suspended_call in self.after_sleep:
            print "suspending %s" % suspended_call.func_name
            suspended_call()
        time.sleep(.01)
        for restarted_call in self.before_sleep:
            print "restarting %s" % restarted_call.func_name
            restarted_call()
        
    def suspend_and_resume(self, method_one, method_two):
        self.before_sleep.append(method_one)
        self.after_sleep.append(method_two)
        
        
class Application(base.Process):
    """a base application object to subclass from.
    
    defunct: used for graphical applications from pygame days"""
    defaults = defaults.Application
    # subclass from me and set some hotkeys!
    
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
            
                
class Messenger(base.Process):

    defaults = defaults.Messenger
    
    def __init__(self, *args, **kwargs):
        super(Messenger, self).__init__(*args, **kwargs)
        self.conversations = {}
                       
        Event("Network_Manager0", "create", "networklibrary.Server", incoming=self._receive_message,\
        outgoing=self._send_message, on_connection=self.register_connection, port=41337, name="Messenger").post()
        
    def _receive_message(self, sock):
        data = sock.recv(1024)
        if not data:
            print "%s disconnected" % sock.getpeername()
            sock.close()
            sock.delete()
        print "%s: %s" % (sock.getpeername(), data)
        Event("Network_Manager0", "buffer_data", sock, data).post()
        
    def _send_message(self, sock, data):
        sock.send(data)
                
    def run(self):
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Messenger0", "run").post()
        else:
            Event("Network_Manager0", "delete_server", "Messenger").post()
            
    def register_connection(self, connection, address):
        print "You may now speak with %s via %s.send..." % (address, self)
        self.conversations[address] = connection
    
    def send(self, message):
        destination, text = "".join(message).split("<")
        ip, port = destination.split(":")
        port = int(port)
        connection = self.conversations[(str(ip), port)]
        print "sending", text, "to", destination
        Event("Network_Manager0", "buffer_data", connection, text).post()
  
    
class Explorer(Application):
    """defunct graphical application from pygame days. Will be reworked
    when graphical applications are worked back in"""
    defaults = defaults.Explorer
    
    def __init__(self, *args, **kwargs):
        super(Explorer, self).__init__(*args, **kwargs)
        self.homescreen = proxy(self.create("widgetlibrary.Homescreen"))
        self.time_service()
        Event("Organizer0", "pack", self).post()
        Event("Display0", "draw", self).post()
                
    def run(self):        
        if self in self.parent.objects[self.__class__.__name__]:
            Event("Explorer0", "run").post()
                           
    def _draw(self):
        return self.homescreen._draw()   