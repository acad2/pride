mpre.audio.portaudiodevices
========
No documentation available

ArgumentError
--------
No documentation available

Array
--------
XXX to be provided

Audio_Device
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- data_source              
- source_name              
- format                   8
- deleted                  False
- data                     
- verbosity                
- record_to_disk           False
- memory_size              16384
- frame_count              0

This object defines the following non-private methods:


- **handle_audio**(self, sender, packet):

		  No documentation available



- **open_stream**(self):

		  No documentation available



- **add_listener**(self, sender, packet):

		  No documentation available



- **get_data**(self):

		  No documentation available



- **handle_data**(self, audio_data):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Input
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- data_source              
- source_name              
- format                   8
- deleted                  False
- frame_count              0
- verbosity                
- record_to_disk           False
- memory_size              16384
- input                    True
- _data                    
- data                     

This object defines the following non-private methods:


- **get_data**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Input', class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Audio_Output
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- frames_per_buffer        1024
- data_source              
- source_name              
- format                   8
- deleted                  False
- frame_count              0
- verbosity                
- mute                     False
- record_to_disk           False
- memory_size              16384
- output                   True
- data                     

This object defines the following non-private methods:


- **handle_audio**(self, sender, packet):

		  No documentation available



- **write_audio**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.audio.portaudiodevices.Audio_Output', class 'mpre.audio.portaudiodevices.Audio_Device', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


BigEndianStructure
--------
Structure with big endian byte order

CDLL
--------
An instance of this class represents a loaded dll/shared
    library, exporting functions using the standard C calling
    convention (named 'cdecl' on Windows).

    The exported functions can be accessed as attributes, or by
    indexing with the function name.  Examples:

    <obj>.qsort -> callable object
    <obj>['qsort'] -> callable object

    Calling the functions releases the Python GIL during the call and
    reacquires it afterwards.
    

FormatError
--------
No documentation available

HRESULT
--------
No documentation available

Instruction
--------
 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Latency
--------
No documentation available

LibraryLoader
--------
No documentation available

LittleEndianStructure
--------
Structure base class

OleDLL
--------
This class represents a dll exporting functions using the
        Windows stdcall calling convention, and returning HRESULT.
        HRESULT error values are automatically raised as WindowsError
        exceptions.
        

PyDLL
--------
This class represents the Python library itself.  It allows to
    access Python API functions.  The GIL is not released, and
    Python exceptions are handled correctly.
    

Structure
--------
Structure base class

Union
--------
Union base class

WinDLL
--------
This class represents a dll exporting functions using the
        Windows stdcall calling convention.
        

c_bool
--------
No documentation available

c_byte
--------
No documentation available

c_char
--------
No documentation available

c_char_p
--------
No documentation available

c_double
--------
No documentation available

c_float
--------
No documentation available

c_int
--------
No documentation available

c_int16
--------
No documentation available

c_int32
--------
No documentation available

c_int64
--------
No documentation available

c_int8
--------
No documentation available

c_long
--------
No documentation available

c_longdouble
--------
No documentation available

c_longlong
--------
No documentation available

c_short
--------
No documentation available

c_size_t
--------
No documentation available

c_ssize_t
--------
No documentation available

c_ubyte
--------
No documentation available

c_uint
--------
No documentation available

c_uint16
--------
No documentation available

c_uint32
--------
No documentation available

c_uint64
--------
No documentation available

c_uint8
--------
No documentation available

c_ulong
--------
No documentation available

c_ulonglong
--------
No documentation available

c_ushort
--------
No documentation available

c_void_p
--------
No documentation available

c_voidp
--------
No documentation available

c_wchar
--------
No documentation available

c_wchar_p
--------
No documentation available

py_object
--------
No documentation available