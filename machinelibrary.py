import base
import eventlibrary
import defaults
import sys
import os
import atexit
Event = eventlibrary.Event
try:
    from windowskeyboard import Keyboard
except:
    import posixkeyboard
    Keyboard = posixkeyboard.Keyboard
    posixkeyboard.toggle_echo(sys.stdin.fileno(), False)
    atexit.register(posixkeyboard.toggle_echo, sys.stdin.fileno(), True)
    
class Machine(base.Base):
    
    defaults = defaults.Machine
    
    def __init__(self, *args, **kwargs):
        super(Machine, self).__init__(*args, **kwargs)
         
        for system_name, args, kwargs in self.system_configuration:
            globals()[system_name] = self.create(system_name, *args, **kwargs)
            
        systems = self.objects["System"]
        for device_name, args, kwargs in self.hardware_configuration:
            hardware_device = self.create(device_name, *args, **kwargs)
            for system in systems:
                if device_name in system.initial_hardware:
                    hardware_device.parent = system
                    system.add(hardware_device)
            hardware_device.parent = base.proxy(self)
                 
    def run(self):       
        while True:
            for system in self.objects["System"]:
                next(system.thread)