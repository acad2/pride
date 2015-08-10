gui.sdllibrary
==============



Font_Manager
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'default_background': (0, 0, 0),
	 'default_color': (150, 150, 255),
	 'default_font_size': 14,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'font_path': 'c:\\users\\_\\pythonbs\\mpre\\gui\\resources\\fonts\\Aero.ttf',
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'gui.sdllibrary.Font_Manager'>,
	 <class 'gui.sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Instruction
--------------

	 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority,
                                                    callback=callback,
                                                    host_info=(ip, port))
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        host_info may supply an ip address string and port number integer
        to execute the instruction on a remote machine. This requirements
        for this to be a success are:
            
            - The machine must have an instance of metapython running
            - The machine must be accessible via the network
            - The local machine must be registered and logged in to
              the remote machine
            - The local machine may need to be registered and logged in to
              have permission to the use the specific component and method
              in question
            - The local machine ip must not be blacklisted by the remote
              machine.
            - The remote machine may require that the local machine ip
              be in a whitelist to access the method in question.
              
        Other then the security requirements, remote procedure calls require 
        zero config on the part of either host. An object will be accessible
        if it exists on the machine in question.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed if the instruction is being executed
        locally. If the instruction is being executed remotely, this instead
        acts as a flag. If set to a True value, the instruction will be
        placed at the front of the local queue to be sent to the host.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds or sent to the machine in question. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'mpre.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback, host_info, transport_protocol):

		 usage: instruction.execute(priority=0.0, callback=None,
                                       host_info=tuple())
        
            Submits an instruction to the processing queue. If being executed
            locally, the instruction will be executed in priority seconds. 
            An optional callback function can be provided if the return value 
            of the instruction is needed.
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If being executed remotely, 
            priority is a high_priority flag where 0 means the instruction will
            be placed at the end of the rpc queue for the remote host in 
            question. If set, the instruction will instead be placed at the 
            beginning of the queue.
            
            Remotely executed instructions have a default callback, which is 
            the appropriate RPC_Requester.alert.
            
            The transport protocol flag is currently unused. Support for
            UDP and other protocols could be implemented and dispatched
            via this flag.


Renderer
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'blendmode_flag': 1,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'flags': 2,
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'gui.sdllibrary.Renderer'>,
	 <class 'gui.sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **draw**(self, texture, draw_instructions, background):

				No documentation available


- **set_render_target**(self, texture):

				No documentation available


- **draw_rect_width**(self, area, **kwargs):

				No documentation available


- **merge_layers**(self, textures):

				No documentation available


- **draw_text**(self, area, text, **kwargs):

				No documentation available


SDL_Component
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'gui.sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

SDL_User_Input
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 '_ignore_click': False,
	 'active_item': None,
	 'auto_start': True,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'event_verbosity': 0,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'run_callback': None,
	 'running': True}

Method resolution order: 

	(<class 'gui.sdllibrary.SDL_User_Input'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_unhandled_event**(self, event):

				No documentation available


- **run**(self):

				No documentation available


- **handle_mousebuttonup**(self, event):

				No documentation available


- **handle_mousemotion**(self, event):

				No documentation available


- **handle_quit**(self, event):

				No documentation available


- **handle_mousebuttondown**(self, event):

				No documentation available


- **handle_mousewheel**(self, event):

				No documentation available


- **handle_keydown**(self, event):

				No documentation available


- **handle_keyup**(self, event):

				No documentation available


- **get_hotkey**(self, instance, key_press):

				No documentation available


SDL_Window
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'area': (0, 0, 800, 600),
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'h': 600,
	 'name': 'Metapython',
	 'position': (0, 0),
	 'priority': 0.04,
	 'renderer_flags': 10,
	 'replace_reference_on_load': True,
	 'showing': True,
	 'size': (800, 600),
	 'w': 800,
	 'window_flags': None,
	 'x': 0,
	 'y': 0,
	 'z': 0}

Method resolution order: 

	(<class 'gui.sdllibrary.SDL_Window'>,
	 <class 'gui.sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **set_layer**(self, instance, value):

				No documentation available


- **run**(self):

				No documentation available


- **remove**(self, instance):

				No documentation available


- **invalidate_layer**(self, layer):

				No documentation available


- **get_mouse_position**(self):

				No documentation available


- **get_mouse_state**(self):

				No documentation available


- **create**(self, *args, **kwargs):

				No documentation available


- **remove_from_layer**(self, instance, z):

				No documentation available


- **add**(self, instance):

				No documentation available


- **pack**(self, modifiers):

				No documentation available


Sprite_Factory
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'gui.sdllibrary.Sprite_Factory'>,
	 <class 'gui.sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Window_Handler
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'gui.sdllibrary.Window_Handler'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **handle_maximized**(self, event):

				No documentation available


- **handle_shown**(self, event):

				No documentation available


- **handle_restored**(self, event):

				No documentation available


- **handle_focus_gained**(self, event):

				No documentation available


- **handle_hidden**(self, event):

				No documentation available


- **handle_resized**(self, event):

				No documentation available


- **handle_size_changed**(self, event):

				No documentation available


- **handle_minimized**(self, event):

				No documentation available


- **handle_focus_lost**(self, event):

				No documentation available


- **handle_leave**(self, event):

				No documentation available


- **handle_event**(self, event):

				No documentation available


- **handle_exposed**(self, event):

				No documentation available


- **handle_close**(self, event):

				No documentation available


- **handle_enter**(self, event):

				No documentation available


- **handle_moved**(self, event):

				No documentation available
