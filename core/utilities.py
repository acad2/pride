#   mpf.utilities - shell commands, arg parser, latency measurement, 
#                    file server,  uploads/downloads, running average
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
import subprocess
from collections import deque

import base
import defaults

Event = base.Event

def shell(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    
def get_arguments(argument_info, **kwargs):
    arguments = {}
    parser = argparse.ArgumentParser(**kwargs)    
    argument_names = argument_info.keys()
    argument_defaults = argument_info.values()
    
    for index, name in enumerate(argument_names):
        if name[0] == "-":
            short_name = name[1]
            long_name = name[1:]
        else:
            short_name = "-" + name[0]
            long_name = "--" + name
        names = (short_name, long_name)      
        default_value = argument_defaults[index]
        variable_type = type(default_value)
        if variable_type == bool:
            variable_type = int            
        for arg_name in names:
            attribute = long_name.replace("-", '')
            info = {}
            if variable_type is type(None):
                arg_name = attribute
            else:
                info.update({"dest" : attribute, 
                             "default" : default_value,
                             "type" : variable_type})
            arguments[arg_name] = info
            
    for argument_name, options in arguments.items():
        parser.add_argument(argument_name, **options)
    return parser.parse_args()
    
def get_options(argument_info, **kwargs):
    namespace = get_arguments(argument_info, **kwargs)
    options = dict((key, getattr(namespace, key)) for key in namespace.__dict__.keys())
    return options
    
class Latency(object):
    
    def __init__(self, name=None, average_size=20):
        super(Latency, self).__init__()
        self.name = name
        self.latency = 0.0
        self.now = time.clock()
        self.max = 0.0
        self.average = Average(size=average_size)
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
        
    def __init__(self, name='', size=20, values=None):
        if not values:
            values = []
        self.name = name
        self.values = deque(values, size)
        self.max_size = size
        self.size = float(len(self.values))
        if self.size:
            self.average = sum(self.values) / self.size
        else:
            self.average = 0
        self.add = self.partial_add
            
    def partial_add(self, value):
        self.size += 1
        self.values.append(value)
        self.average = sum(self.values) / self.size
        if self.size == self.max_size:
            self.add = self.full_add
        
    def full_add(self, value):
        old_value = self.values[0]
        adjustment = (value - old_value) / self.size
        self.values.append(value)
        self.average += adjustment        


class File_Server(base.Base):

    defaults = defaults.File_Server
    
    def __init__(self, **kwargs):
        super(File_Server, self).__init__(**kwargs)     
        
        if self.asynchronous_server:
            options = {"interface" : self.interface,
                       "port" : self.port, 
                       "name" : "File_Server", 
                       "inbound_connection_type" : "networklibrary.Upload"}                           
            Event("Asynchronous_Network0", "create", "networklibrary.Server", **options).post()    

    def send_file(self, filename='', ip='', port=40021, show_progress=True):
        to = (ip, port)
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.connect(to)
        with open(filename, "rb") as data_file:
            data = data_file.read()
            data_file.close()
        file_size = len(data)
        latency = Latency(name="send_file %s" % filename)
        frame_time = Average(size=100)
        upload_rate = Average(size=10)
        started_at = time.clock()
        while data:
            amount_sent = sender.send(data[:self.network_chunk_size])            
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
        if getattr(self, "exit_when_finished", None):
            sys.exit()

    def receive_file(self, filename='', interface="0.0.0.0", port=40021, show_progress=True):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((interface, port))
        server.listen(1)        
        _file = open(filename, "wb")
        frame_time = Average(size=100)
        download_rate = Average(size=10)
        latency = Latency(name="receive_file %s" % filename)
        downloading = True
        started_at = time.clock()
        data_size = 0
        print "waiting for connection...", interface, port
        receiver, _from = server.accept()
        print "Received"
        receiver.settimeout(2)
        while downloading:
            latency.update()
            data = receiver.recv(self.network_chunk_size)
            if not data:
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
        sys.stdout.write("\b"*80)
        print "\nDownload of %s complete (%s bytes in %s seconds)" % \
        (filename, data_size, (time.clock() - started_at - 2.0))
        _file.close()
        receiver.close()
        server.close()
        if getattr(self, "exit_when_finished", None):
            sys.exit()

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
    
        