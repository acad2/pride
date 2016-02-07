Gui Programming
---------
For each lesson, create a file called lesson_number_x.py, where 'x' is replaced
by the lesson number. Enter the code for each lesson into the appropriate file,
and run the file with the command "python -m pride.main lesson_number_x.py".

These lessons assume a basic grasp of the python language. For a beginners
introduction to the language, consult the python documentation or various
books and websites dedicated to the topic.

Lesson One
-------
In this lesson we will enable the graphical user interface and make a window 
appear on the screen.

    import pride.gui
    pride.gui.enable() # this opens the window
    
    
Hopefully that has you saying "That was easy". Plenty more to go!
    
    
Lesson Two
------
In this lesson we will learn how to create objects that can be seen and
interacted with via the mouse.

    import pride.gui.gui # this contains things like buttons, windows, and application object