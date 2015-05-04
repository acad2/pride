widgetlibrary
==============



Attribute_Displayer
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

	(<class 'widgetlibrary.Attribute_Displayer'>,
	 <class 'mpre.gui.guilibrary.Window'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Date_Time_Button
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
	 'pack_mode': 'horizontal',
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

	(<class 'widgetlibrary.Date_Time_Button'>,
	 <class 'mpre.gui.guilibrary.Button'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **update_time**(self):

		No documentation available


Homescreen
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'background_color': (0, 0, 0),
	 'background_filename': 'C:\\test.jpg',
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

	(<class 'widgetlibrary.Homescreen'>,
	 <class 'mpre.gui.guilibrary.Window'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Indicator
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

	(<class 'widgetlibrary.Indicator'>,
	 <class 'mpre.gui.guilibrary.Button'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **draw_texture**(self):

		No documentation available


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


Popup_Menu
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
	 'pack_modifier': <function <lambda> at 0x026ED170>,
	 'pack_on_init': True,
	 'popup': True,
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'show_title_bar': False,
	 'size': [800, 600],
	 'verbosity': '',
	 'x': 0,
	 'y': 0}

Method resolution order: 

	(<class 'widgetlibrary.Popup_Menu'>,
	 <class 'mpre.gui.guilibrary.Container'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Right_Click_Button
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

	(<class 'widgetlibrary.Right_Click_Button'>,
	 <class 'mpre.gui.guilibrary.Button'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **click**(self, mouse):

		No documentation available


Right_Click_Menu
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
	 'pack_mode': 'layer',
	 'pack_modifier': <function <lambda> at 0x026ED170>,
	 'pack_on_init': True,
	 'popup': True,
	 'replace_reference_on_load': True,
	 'sdl_window': 'SDL_Window',
	 'show_title_bar': False,
	 'size': (200, 150),
	 'verbosity': '',
	 'x': 0,
	 'y': 0}

Method resolution order: 

	(<class 'widgetlibrary.Right_Click_Menu'>,
	 <class 'widgetlibrary.Popup_Menu'>,
	 <class 'mpre.gui.guilibrary.Container'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Task_Bar
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
	 'pack_mode': 'menu_bar',
	 'pack_modifier': <function <lambda> at 0x026ED1B0>,
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

	(<class 'widgetlibrary.Task_Bar'>,
	 <class 'mpre.gui.guilibrary.Container'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

Title_Bar
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

	(<class 'widgetlibrary.Title_Bar'>,
	 <class 'mpre.gui.guilibrary.Container'>,
	 <class 'mpre.gui.guilibrary.Window_Object'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **draw_texture**(self):

		No documentation available
