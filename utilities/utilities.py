#   mpf.utilities - latency measurement, file up/downloads, running average
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

import socket
import sys
import os
import time
import argparse
from collections import deque

import base
import defaults

Event = base.Event

def get_arguments(argument_names, argument_defaults, **kwargs):
    arguments = {}
    parser = argparse.ArgumentParser(**kwargs)
    for index, names in enumerate(argument_names):
        short_name, long_name = names
        default_value = argument_defaults[index]
        for arg_name in names:
            arguments[arg_name] = {"dest" : long_name.replace("-", ""), "default" : default_value}
    for argument_name, options in arguments.items():
        parser.add_argument(argument_name, **options)  
    return parser.parse_args()
    
class Latency(object):
    
    def __init__(self, name=None):
        super(Latency, self).__init__()
        self.name = name
        self.latency = 0.0
        self.now = time.clock()
        self.max = 0.0
        self.average = Average(size=20)
        self._position = 0

    def update(self):
        self._position += 1
        time_before = self.time_before = self.now
        now = self.now = time.clock()
        latency = now - time_before
        self.average.add(latency)
        if (self._position == 20 or latency > self.max):
            self.max = latency
            self._position = 0
        self.latency = latency

    def display(self, mode="sys.stdin"):
        if "print" in mode:
            print "%s Latency: %0.6f, Average: %0.6f, Max: %0.6f" % \
            (self.name, self.latency, self.average.average, self.max)
        else:
            sys.stdout.write("\b"*120)
            sys.stdout.write("%s Latency: %0.6f, Average: %0.6f, Max: %0.6f" % \
            (self.name, self.latency, self.average.average, self.max))
            
            
class Average(object):
        
    def __init__(self, values=None, size=20):
        if not values:
            values = []
        self.values = deque(values, size)
        self.max_size = size
        self.size = float(len(self.values))
        if self.size:
            self.average = sum(self.values) / self.size
        else:
            self.average = 0
     
    def add(self, value):
        if self.size == self.max_size:
            self.full_add(value)
        else:
            self.partial_add(value)
            
    def partial_add(self, value):
        self.size += 1
        self.values.append(value)
        self.average = sum(self.values) / self.size
        
    def full_add(self, value):
        old_value = self.values[0]
        adjustment = (value - old_value) / self.size
        self.values.append(value)
        self.average += adjustment        


class File_Manager(base.Base):

    defaults = defaults.File_Manager
    
    def __init__(self, **kwargs):
        super(File_Manager, self).__init__(**kwargs)        
        if self.asynchronous_server:
            options = {"port" : self.port, 
                       "name" : "File_Manager", 
                       "inbound_connection_type" : "networklibrary.Upload"}                           
            Event("Asynchronous_Network0", "create", "networklibrary.Server", **options).post()    

    def send_file(self, filename, address, port=40021, show_progress=True):
        to = (address, port)
        sender = self.create("networklibrary.UDP_Socket", port=40021)
        data = open(filename, "rb").read()
        file_size = len(data)
        latency = Latency(name="send_file %s" % filename)
        frame_time = Average(size=100)
        upload_rate = Average(size=10)
        started_at = time.clock()
        while data:
            amount_sent = sender.sendto(data[:self.network_chunk_size], to)            
            data = data[self.network_chunk_size:]
            if show_progress:
                latency.update()
                upload_rate.add(amount_sent)
                frame_time.add(latency.latency)
                data_size = len(data)
                chunks_per_second = 1.0 / frame_time.average
                bytes_per_second = chunks_per_second * upload_rate.average
                time_remaining = (data_size / bytes_per_second)
                sys.stdout.write("\b"*80)
                sys.stdout.write("Upload rate: %iB/s. Time remaining: %i" % (bytes_per_second, time_remaining))
        print "\n%s bytes uploaded in %s seconds" % (file_size, time.clock() - started_at)
        sender.close()

    def receive_file(self, filename, address=("0.0.0.0", 40021), show_progress=True):
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind(address)
        _file = open(filename, "wb")
        frame_time = Average(size=100)
        download_rate = Average(size=10)
        latency = Latency(name="receive_file %s" % filename)
        downloading = True
        started_at = time.clock()
        data_size = 0
        while downloading:
            latency.update()
            try:
                data, _from = receiver.recvfrom(self.network_chunk_size)
            except socket.error:
                downloading = False
            amount_received = len(data)
            download_rate.add(amount_received)
            data_size += amount_received
            receiver.settimeout(2)
            _file.write(data)
            _file.flush()
            if show_progress:
                frame_time.add(latency.latency)
                chunks_per_second = 1.0 / frame_time.average
                bytes_per_second = chunks_per_second * download_rate.average
                sys.stdout.write("\b"*80)
                sys.stdout.write("Downloading at %iB/s" % bytes_per_second)
        print "\nDownload of %s complete (%s bytes in %s seconds)" % \
        (filename, data_size, time.clock() - started_at)
        _file.close()
        receiver.close()
        

class Updater(object):
                
    def __init__(self):
        super(Updater, self).__init__()
        
    def live_update(self, component_name, source):
        """Updates base component component_name with a class specified in source."""
        new_component_name = source[source.find("class ")+6:source.find("(")] # scoops Name from "class Name(object):"
        code = compile(source, "update", "exec")
        old_component = base.Component_Resolve[component_name]  
        exec code in locals(), globals()
        new_component_class = locals()[new_component_name]
        options = {"component" : old_component.parent} # for the Event, not actually an instance option
        for attribute_name in dir(old_component):
            if "__" not in attribute_name:
                value = getattr(old_component, attribute_name)
                if not callable(value):
                    options[attribute_name] = value
        new_component = old_component.parent.create(new_component_class, **options)
        base.Component_Resolve[component_name] = new_component
    
        