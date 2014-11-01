#   mpf.keyboard - non blocking user input (eventually!)
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
try:
    from msvcrt import kbhit as input_waiting
except:
    from select import select
    def input_waiting():
        return select([sys.stdin], [], [], 0.0)[0]
        
import select
import base
import defaults

class Keyboard(base.Hardware_Device):
    
    defaults = defaults.Keyboard
    
    def __init__(self, *args, **kwargs):
        super(Keyboard, self).__init__(*args, **kwargs)
        self.characters = ''
        
    def input_waiting(self):
        return (self.characters or input_waiting())
    
    def get_line(self):
        characters = self.characters
        self.characters = ''
        return characters
        
    def get_character(self):
        try:
            character = self.characters[0]
            self.characters = self.characters[1:]
        except IndexError:
            if self.input_waiting():
                self.characters = self.capture_input()
            else:
                self.characters = ''
            character = ''
        return character
                
    def capture_input(self):
        return sys.stdin.readline()
            
"""
class Keyboard(base.Hardware_Device):
    
    defaults = defaults.Keyboard
    
    input_waiting = kbhit
    _get_input = getwch
    
    def __init__(self, *args, **kwargs):
        super(Keyboard, self).__init__(*args, **kwargs)
        self.thread = self.new_thread()
      
    def get_input(self):
        return next(self.thread)
        
    def new_thread(self):
        while True:
            yield self._get_input()
            
    def run(self):
        if self.input_waiting:
            active_item = self.parent.active_item
            hotkey = self.get_hotkey(active_item, self.get_input())
            if hotkey:
                hotkey.post()

        if self in self.parent.objects[self.__class__.__name__]:
            Event("Keyboard", "run").post()
   
    def get_hotkey(self, key, instance):
        if instance is None:
            return None

        hotkey = instance.hotkeys.get(key)
        if not hotkey:
            try:
                hotkey = self.get_hotkey(getattr(instance, "parent"), key)
            except AttributeError:
                self.warning("could not find hotkey from %s or parent" % instance, "Audit: ")

        return hotkey            
        """