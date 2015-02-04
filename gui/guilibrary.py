import heapq
import ctypes
from operator import attrgetter
from sys import modules
from math import floor, sqrt

import mpre.base as base
import mpre.vmlibrary as vmlibrary
import defaults
import mpre.utilities as utilities
Instruction = base.Instruction

import sdl2
import sdl2.ext
SDL_Rect = sdl2.SDL_Rect

R, G, B, A = 0, 80, 255, 30
dark_color_scalar = .5
light_color_scalar = 1.5


# provides the pack() functionality
class Organizer(vmlibrary.Process):

    defaults = defaults.Organizer

    def __init__(self, *args, **kwargs):
        super(Organizer, self).__init__(*args, **kwargs)
        self.queue = []
        self.running = False

    def pack(self, item):
        #print "adding to pack queue", item
        self.queue.append(item)
        if not self.running:
            self.running = True
            self.process("run")

    def run(self):
        queue = self.queue
        while queue:
            item = queue.pop(0)
            print "packing", item.instance_name, item.pack_mode
            print "stats before: ", item.area, item.layer
            parent_queue = item.parent.draw_queue
            try:
                count = parent_queue.index(item)
                length = len(parent_queue)
            except ValueError:
                count = 0
                length = 1
            pack = getattr(self, "pack_{0}".format(item.pack_mode))
            pack(item, count, length)
            print "stats after: ", item.area, item.layer
        self.running = False

    def pack_horizontal(self, item, count, length):
        parent = item.parent
        item.layer = parent.layer + 1
        item.size = (parent.size[0]/length, parent.size[1])
        item.x = (item.size[0]*count)+parent.x
        item.y = parent.y

    def pack_vertical(self, item, count, length):
        parent = item.parent
        item.layer = parent.layer + 1
        item.size = (parent.size[0], parent.size[1]/length)
        item.y = (item.size[1]*count)+parent.y
        item.x = parent.x

    def pack_grid(self, item, count, length):
        grid_size = sqrt(length)

        if grid_size != floor(grid_size):
            grid_size = floor(grid_size)+1

        position = (int(floor((count / grid_size))), (count % grid_size))

        parent = item.parent
        item.layer = parent.layer + 1
        item.size = int(parent.size[0]/grid_size), int(parent.size[1]/grid_size)
        item.x = (item.size[0]*position[1])+parent.x
        item.y = (item.size[1]*position[0])+parent.y

    def pack_text(self, item, count, length):
        parent = item.parent
        item.layer = parent.layer + 1
        item.x = parent.x + parent.x_width + parent.x_spacing
        item.y = parent.y

    def pack_menu_bar(self, item, count, length):
        parent = item.parent
        item.layer = parent.layer + 1
        item.x = parent.x
        item.y = parent.y
        item.size = (parent.size[0], int(parent.size[1]*.03))

    def pack_layer(self, item, count, length):
        parent = item.parent
        item.layer = parent.layer + 1

    #def pack_center(self, item):
     #   item.x = Display.SCREEN_SIZE[0]/2
      #  item.y = Display.SCREEN_SIZE[1]/2



class Window_Object(base.Base):

    # default values
    defaults = defaults.Window_Object
    Hotkeys = {}
    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, position):
        self.x, self.y = position
    position = property(_get_position, _set_position)

    def _get_area(self):
        size = self.size
        return (self.x, self.y, size[0], size[1])
    def _set_area(self, rect):
        self.position, self.size = rect
    area = property(_get_area, _set_area)

    # calculates the outline color
    def _get_outline_color(self):
        return (int(self.color[0]*self.color_scalar), int(self.color[1]*\
        self.color_scalar), int(self.color[2]*self.color_scalar))

    outline_color = property(_get_outline_color)

    def _get_rect(self):
        return sdl2.SDL_Rect(*self.area)
    rect = property(_get_rect)

    def __init__(self, **kwargs):
        self.draw_queue = []
        super(Window_Object, self).__init__(**kwargs)

     #   if self.draw_on_init:
      #      self.draw_texture()

    def create(self, *args, **kwargs):
        kwargs["sdl_window"] = self.sdl_window
        kwargs["layer"] = self.layer + 1
        instance = super(Window_Object, self).create(*args, **kwargs)

        if hasattr(instance, "draw_texture"):
            self.draw_queue.append(instance)
            instance.added_to.add(self.instance_name)
        return instance

    def press(self, mouse):
        self.held = True

    def release(self, mouse):
        self.held = False
        self.click(mouse)

    def click(self, mouse):
        if mouse.button == 3:
            args = (self.instance_name, "create", "widgetlibrary.Right_Click_Menu")
            options = {"x" : mouse.x,
                       "y" : mouse.y,
                       "target" : self}
            Instruction(*args, **options).execute()
            draw = Instruction(self.instance_name, "draw_texture")
            draw.component = self
            draw.execute()

    def mousewheel(self, x_amount, y_amount):
        pass

    def mousemotion(self, x_change, y_change):
        if self.held:
            self.draw("fill", self.area, color=self.parent.color)
            self.x += x_change
            self.y += y_change
            for item in self.draw_queue:
                original = item.held
                item.held = True
                item.mousemotion(x_change, y_change)
                item.held = original
            try:
                self.parent.draw_texture()
            except AttributeError:
                self.draw_texture()

    def draw(self, figure="rect", *args, **kwargs):
        Instruction(self.sdl_window, "draw", self.instance_name, figure, self.area, self.layer, *args, **kwargs).execute()

    def draw_texture(self):
        area = self.area
        draw = self.draw
        draw("fill", area, color=self.color)
        draw("rect", area, color=self.outline_color)
        for item in self.draw_queue:
            item.draw_texture()

    def pack(self, reset=False):
        if reset:
            self.x = self.y = 0
        Instruction("Organizer", "pack", self).execute()
        for item in self.draw_queue:
            item.pack()

    def delete(self):
        self.parent.draw_queue.remove(self)
        super(Window_Object, self).delete()


class Window(Window_Object):

    defaults = defaults.Window

    def __init__(self, **kwargs):
        super(Window, self).__init__(**kwargs)

       # if getattr(self, "title_bar", None):
        #    self.create("widgetlibrary.Title_Bar")


class Container(Window_Object):

    defaults = defaults.Container

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)


class Button(Window_Object):

    defaults = defaults.Button

    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)

    def draw_texture(self):
        super(Button, self).draw_texture()
        self.draw("text", self.text, self.area, color=self.text_color)
