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
    from msvcrt import getwch, kbhit
    input_waiting = kbhit
except:
    def input_waiting():
        return select.select([sys.stdin], [], [], 0.0)[0]
        
import select
from threading import Thread

import vmlibrary
import defaults

class Keyboard(vmlibrary.Hardware_Device):
    
    defaults = defaults.Keyboard
    
    def __init__(self, **kwargs):
        super(Keyboard, self).__init__(**kwargs)
        self.characters = ''
        self.getting_input = False
        self.reader_thread = Thread(target=self.raw_input)
        self.receivers = set()
        
    def input_waiting(self):
        return (self.characters or input_waiting())
    
    def get_line(self, receiver):
        self.receivers.add(receiver)
        if not self.getting_input:
            self.getting_input = True
            self.reader_thread.start()
                        
    def raw_input(self):
        characters = sys.stdin.readline()
        for receiver in self.receivers:
            receiver.keyboard_input += characters
        self.reader_thread = Thread(target=self.raw_input)
        self.getting_input = False