guilibrary
==============



Button
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'alpha': 1,
	 'background_color': (0, 0, 0),
	 'color': (0, 115, 10),
	 'color_scalar': 0.6,
	 'held': False,
	 'layer': 1,
	 'outline_width': 5,
	 'pack_mode': 'vertical',
	 'pack_modifier': '',
	 'pack_on_init': True,
	 'popup': False,
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'shape': 'rect',
	 'show_title_bar': False,
	 'size': [800, 600],
	 'text': 'Button',
	 'text_color': (255, 130, 25),
	 'verbosity': '',
	 'x': 0,
	 'y': 0}

Method resolution order: 

	(<class 'guilibrary.Button'>,
	 <class 'guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **draw_texture**(self):

		No documentation available


Container
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'alpha': 1,
	 'background_color': (0, 0, 0),
	 'color': (0, 115, 10),
	 'color_scalar': 0.6,
	 'held': False,
	 'layer': 1,
	 'outline_width': 5,
	 'pack_mode': 'vertical',
	 'pack_modifier': '',
	 'pack_on_init': True,
	 'popup': False,
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'show_title_bar': False,
	 'size': [800, 600],
	 'verbosity': '',
	 'x': 0,
	 'y': 0}

Method resolution order: 

	(<class 'guilibrary.Container'>,
	 <class 'guilibrary.Window_Object'>,
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


Organizer
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'auto_start': True,
	 'priority': 0,
	 'replace_reference_on_load': True,
	 'verbosity': ''}

Method resolution order: 

	(<class 'guilibrary.Organizer'>, <class 'mpre.base.Base'>, <type 'object'>)

- **pack_menu_bar**(self, item, count, length):

		No documentation available


- **pack_text**(self, item, count, length):

		No documentation available


- **pack_vertical**(self, item, count, length):

		No documentation available


- **pack_layer**(self, item, count, length):

		No documentation available


- **pack_grid**(self, item, count, length):

		No documentation available


- **pack_horizontal**(self, item, count, length):

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

Theme
--------------

	No docstring found


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

	(<class 'guilibrary.Theme'>,
	 <class 'guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **draw_texture**(self, window_object):

		No documentation available


Window
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'background_color': (0, 0, 0),
	 'color': (0, 115, 10),
	 'color_scalar': 0.6,
	 'held': False,
	 'layer': 1,
	 'outline_width': 5,
	 'pack_mode': 'layer',
	 'pack_modifier': '',
	 'pack_on_init': True,
	 'popup': False,
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'show_title_bar': False,
	 'size': [800, 600],
	 'verbosity': '',
	 'x': 0,
	 'y': 0}

Method resolution order: 

	(<class 'guilibrary.Window'>,
	 <class 'guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Window_Object
--------------

	No docstring found


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

	(<class 'guilibrary.Window_Object'>, <class 'mpre.base.Base'>, <type 'object'>)

- **click**(self, mouse):

		No documentation available


- **mousemotion**(self, x_change, y_change):

		No documentation available


- **create**(self, *args, **kwargs):

		No documentation available


- **draw_children**(self):

		No documentation available


- **add**(self, instance):

		No documentation available


- **draw_texture**(self):

		No documentation available


- **draw**(self, figure, *args, **kwargs):

		No documentation available


- **mousewheel**(self, x_amount, y_amount):

		No documentation available


- **press**(self, mouse):

		No documentation available


- **release**(self, mouse):

		No documentation available


- **pack**(self, reset):

		No documentation available


- **delete**(self):

		No documentation available


attrgetter
--------------

	attrgetter(attr, ...) --> attrgetter object

Return a callable object that fetches the given attribute(s) from its operand.
After f = attrgetter('name'), the call f(r) returns r.name.
After g = attrgetter('name', 'date'), the call g(r) returns (r.name, r.date).
After h = attrgetter('name.first', 'name.last'), the call h(r) returns
(r.name.first, r.name.last).


Method resolution order: 

	(<type 'operator.attrgetter'>, <type 'object'>)