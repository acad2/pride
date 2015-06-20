gui.gui
==============



Button
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 '_ignore_click': False,
	 'allow_text_edit': False,
	 'background_color': (25, 25, 45, 255),
	 'button_verbosity': 'v',
	 'color': (155, 155, 255, 255),
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'edit_text_mode': False,
	 'held': False,
	 'outline_width': 5,
	 'pack_mode': 'vertical',
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'shape': 'rect',
	 'size': (800, 600),
	 'text': '',
	 'text_color': (145, 165, 235),
	 'texture': None,
	 'verbosity': '',
	 'x': 0,
	 'y': 0,
	 'z': 0}

Method resolution order: 

	(<class 'gui.gui.Button'>,
	 <class 'gui.gui.Window_Object'>,
	 <class 'mpre.gui.shapes.Bounded_Shape'>,
	 <class 'mpre.gui.shapes.Shape'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Container
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 '_ignore_click': False,
	 'allow_text_edit': False,
	 'background_color': (25, 25, 45, 255),
	 'button_verbosity': 'v',
	 'color': (155, 155, 255, 255),
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'edit_text_mode': False,
	 'held': False,
	 'outline_width': 5,
	 'pack_mode': 'vertical',
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'size': (800, 600),
	 'text': '',
	 'text_color': (145, 165, 235),
	 'texture': None,
	 'verbosity': '',
	 'x': 0,
	 'y': 0,
	 'z': 0}

Method resolution order: 

	(<class 'gui.gui.Container'>,
	 <class 'gui.gui.Window_Object'>,
	 <class 'mpre.gui.shapes.Bounded_Shape'>,
	 <class 'mpre.gui.shapes.Shape'>,
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
            
            host_info may be specified to designate a remote machine that
            the Instruction should be executed on. If host_info is supplied
            and callback is None, the results of the instruction will be 
            supplied to RPC_Handler.alert.


Organizer
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'gui.gui.Organizer'>, <class 'mpre.base.Base'>, <type 'object'>)

- **pack_menu_bar**(self, parent, item, count, length):

				No documentation available


- **pack_horizontal**(self, parent, item, count, length):

				No documentation available


- **pack_vertical**(self, parent, item, count, length):

				No documentation available


- **pack_z**(self, parent, item, count, length):

				No documentation available


- **pack_grid**(self, parent, item, count, length):

				No documentation available


- **pack**(self, item):

				No documentation available


SDL_Rect
--------------

	No documentation available


Method resolution order: 

	(<class 'sdl2.rect.SDL_Rect'>,
	 <type '_ctypes.Structure'>,
	 <type '_ctypes._CData'>,
	 <type 'object'>)

Window
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 '_ignore_click': False,
	 'allow_text_edit': False,
	 'background_color': (25, 25, 45, 255),
	 'button_verbosity': 'v',
	 'color': (155, 155, 255, 255),
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'edit_text_mode': False,
	 'held': False,
	 'outline_width': 5,
	 'pack_mode': 'z',
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'size': (800, 600),
	 'text': '',
	 'text_color': (145, 165, 235),
	 'texture': None,
	 'verbosity': '',
	 'x': 0,
	 'y': 0,
	 'z': 0}

Method resolution order: 

	(<class 'gui.gui.Window'>,
	 <class 'gui.gui.Window_Object'>,
	 <class 'mpre.gui.shapes.Bounded_Shape'>,
	 <class 'mpre.gui.shapes.Shape'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Window_Object
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 '_ignore_click': False,
	 'allow_text_edit': False,
	 'background_color': (25, 25, 45, 255),
	 'button_verbosity': 'v',
	 'color': (155, 155, 255, 255),
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'edit_text_mode': False,
	 'held': False,
	 'outline_width': 5,
	 'pack_mode': '',
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'size': (800, 600),
	 'text': '',
	 'text_color': (145, 165, 235),
	 'texture': None,
	 'verbosity': '',
	 'x': 0,
	 'y': 0,
	 'z': 0}

Method resolution order: 

	(<class 'gui.gui.Window_Object'>,
	 <class 'mpre.gui.shapes.Bounded_Shape'>,
	 <class 'mpre.gui.shapes.Shape'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **pack**(self, modifiers):

				No documentation available


- **left_click**(self, mouse):

				No documentation available


- **mousemotion**(self, x_change, y_change, top_level):

				No documentation available


- **create**(self, *args, **kwargs):

				No documentation available


- **add**(self, instance):

				No documentation available


- **draw_texture**(self):

				No documentation available


- **draw**(self, figure, *args, **kwargs):

				No documentation available


- **mousewheel**(self, x_amount, y_amount):

				No documentation available


- **right_click**(self, mouse):

				No documentation available


- **press**(self, mouse):

				No documentation available


- **glow**(self):

				No documentation available


- **remove**(self, instance):

				No documentation available


- **release**(self, mouse):

				No documentation available


- **delete**(self):

				No documentation available


create_texture
--------------

**create_texture**(size, access):

				No documentation available
