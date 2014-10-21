import sys
import time
from random import randint

import base
import defaults

Event = base.Event

def display_latency():
    time_before = display_latency.time_before = display_latency.now
    now = display_latency.now = time.time()
    latency = now - time_before
    if latency > display_latency.max:
        display_latency.max = latency
    if not randint(0, 256):
        display_latency.max = 0.0
    #print "Latency: %s, Max latency: %s" % (str(latency), str(display_latency.max))
    sys.stdout.write("\b"*120)
    sys.stdout.write("Latency: %0.7f, Max latency: %0.7f" % (latency, display_latency.max))
display_latency.now = time.time()
display_latency.max = 0

def update(component_name, source):
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
    
    
class File_Transfer_Utility(base.Base):
    
    defaults = defaults.File_Transfer_Utility
    
    def __init__(self, *args, **kwargs):
        super(File_Transfer_Utility, self).__init__(*args, **kwargs)
        options = {"port" : self.port, 
        "name" : "File_Transfer_Utility", 
        "inbound_connection_type" : "networklibrary.Upload"}
        
        #self.server = self.create("networklibrary.Server", **options)
        Event("Network_Manager0", "create", "networklibrary.Server", **options).post()  