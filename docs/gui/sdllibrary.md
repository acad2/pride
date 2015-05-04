sdllibrary
==============



Display_Wrapper
--------------

	used by the display internally to display all objects


Instance defaults: 

	{'_deleted': False,
	 'background_color': (0, 0, 0),
	 'color': (0, 115, 10),
	 'color_scalar': 0.6,
	 'held': False,
	 'layer': 1,
	 'outline_width': 5,
	 'pack_mode': '',
	 'pack_modifier': '',
	 'pack_on_init': True,
	 'popup': False,
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'size': [800, 600],
	 'verbosity': '',
	 'x': 0,
	 'y': 0}

Method resolution order: 

	(<class 'sdllibrary.Display_Wrapper'>,
	 <class 'mpre.base.Wrapper'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **press**(self):

		No documentation available


- **click**(self):

		No documentation available


Font_Manager
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'default_background': (0, 0, 0),
	 'default_color': (15, 180, 35),
	 'default_font_size': 14,
	 'font_path': 'c:\\users\\_\\pythonbs\\mpre\\gui\\resources\\fonts\\Aero.ttf',
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'sdllibrary.Font_Manager'>,
	 <class 'sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Instruction
--------------

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
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.


Method resolution order: 

	(<class 'mpre.Instruction'>, <type 'object'>)

- **execute**(self, priority, callback, host_info, transport_protocol):

		 usage: instruction.execute(priority=0.0, callback=None)
        
            Submits an instruction to the processing queue. The instruction
            will be executed in priority seconds. An optional callback function 
            can be provided if the return value of the instruction is needed.


Renderer
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'componenttypes': (),
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'sdllibrary.Renderer'>,
	 <class 'sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **draw_rect_width**(self, area, **kwargs):

		No documentation available


- **draw_text**(self, text, rect, **kwargs):

		No documentation available


SDL_Component
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False, 'replace_reference_on_load': True, 'verbosity': ''}

Method resolution order: 

	(<class 'sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

SDL_User_Input
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_start': True,
	 'priority': 0.04,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'sdllibrary.SDL_User_Input'>,
	 <class 'mpre.vmlibrary.Process'>,
	 <class 'mpre.base.Reactor'>,
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


- **mouse_is_inside**(self, area, mouse_pos_x, mouse_pos_y):

		No documentation available


- **add_popup**(self, item):

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
	 'color': (0, 0, 0),
	 'layer': 0,
	 'name': 'Metapython',
	 'replace_reference_on_load': True,
	 'showing': True,
	 'size': [800, 600],
	 'verbosity': '',
	 'x': 0,
	 'y': 0}

Method resolution order: 

	(<class 'sdllibrary.SDL_Window'>,
	 <class 'sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **draw**(self, item, mode, area, z, *args, **kwargs):

		No documentation available


- **run**(self):

		No documentation available


- **get_mouse_state**(self):

		No documentation available


- **create**(self, *args, **kwargs):

		No documentation available


- **get_mouse_position**(self):

		No documentation available


Sprite_Factory
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False, 'replace_reference_on_load': True, 'verbosity': ''}

Method resolution order: 

	(<class 'sdllibrary.Sprite_Factory'>,
	 <class 'sdllibrary.SDL_Component'>,
	 <class 'mpre.base.Proxy'>,
	 <class 'mpre.base.Reactor'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

itemgetter
--------------

	itemgetter(item, ...) --> itemgetter object

Return a callable object that fetches the given item(s) from its operand.
After f = itemgetter(2), the call f(r) returns r[2].
After g = itemgetter(2, 5, 3), the call g(r) returns (r[2], r[5], r[3])


Method resolution order: 

	(<type 'operator.itemgetter'>, <type 'object'>)