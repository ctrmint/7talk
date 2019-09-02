#! /usr/bin/env python3
# --------------------------------------------------------------
# Pygame gauge library developed for use with ECU Dashboards.
# --------------------------------------------------------------
# Requires import of dash_support for colour definitions.
# Notes.
# Gauges currently use the draw arc function which is bugged, and has an aliasing issue on the screen.
# At present this is expected behaviour.  Yes it sucks!
# ---------------------------------------------------------------

import math
from dash_support import *
from colours import *
import pygame
from pygame.locals import *


class DisplayTraceGauge(object):
    """ A class for a trace gauge
        Draws a trace of the data value show.

        wsurface = the pygame surface.
        copyrectangle = rectangular screen area to be move to the left.
        gaugeheight = the height of the gauage, needs to fit below other screen assets, 100 recommended
        colours = list of two colours, line colour and the wipe colour.
        maxminvallist = max and min values possible in the gauge, required to determine % of the overall
        gauge height per data value.
        solid = changes inc, which in terns changes with the area under the graph is solid.
        graded = colour gradient introduced for plot points, also adds white for 90th percentile.


    """

    def __init__(self, wsurface, copyrectangle, gaugeheight, colours, maxminvallist, solid, graded):
        self.surface = wsurface
        self.datavalue = 0
        self.gaugeheight = gaugeheight
        self.line_colour = colours[0]
        self.wipecolour = colours[1]
        self.copy_rect_x = copyrectangle[0]
        self.copy_rect_y = copyrectangle[1]
        self.maxval = maxminvallist[0]
        self.minval = maxminvallist[1]
        self.current_pair = [0, 0]
        self.baseline = display_height - 16
        self.solid = solid
        self.graded = graded
        self.inc = 2
        if self.solid:
            self.inc = 1

    def update(self, data):
        dataplotheight = (data / self.maxval) * self.gaugeheight
        self.current_pair[0] = data
        self.current_pair[1] = dataplotheight
        self.scroll_left()
        return

    def scroll_left(self):
        x = display_width - self.inc
        y = self.baseline - self.current_pair[1]
        if self.graded:
            temp_colour_list = list(self.line_colour)
            if self.current_pair[1] > 90:
                self.line_colour = WHITE
            else:
                y_colour = (self.current_pair[1] / self.gaugeheight * 200) + 50
                temp_colour_list[0] = 0
                temp_colour_list[2] = 0
                temp_colour_list[1] = y_colour
                if temp_colour_list[1] > 255:
                    temp_colour_list[1] = 255
                self.line_colour = tuple(temp_colour_list)

        pygame.draw.line(self.surface, BLACK, (x, y), (x, (self.baseline-self.gaugeheight)))
        pygame.draw.line(self.surface, self.line_colour, (x, y), (x, y))
        area_rect = pygame.Rect(self.copy_rect_x, self.copy_rect_y, display_width, self.gaugeheight)
        area = self.surface.subsurface(area_rect)
        area.scroll(-1, 0)
        return

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class DisplayDialGauge(object):
    """
        A gauge class built using Pygame draw arc function.
        Gauge uses an inner and outer arc to define the bounds of the gauge
        A gauge line is then used to define the maximum plot, which then masked in reverse to denote the actual value.

        requires.
            window surface, outer arc square dimensions as list, border thickness, and border colour

        Note.
            Needs making more generic for general use, some values have been hard coded during development.
    """
    data_per_degree = max_rpm / 225
    horizontal_line_in_rpm = 180 * data_per_degree
    PI = math.pi

    def __init__(self, wsurface, outer_arc_square, border_thickness, border_colour):
        self.data_value = 0
        self.outer_arc_square = outer_arc_square
        self.surface = wsurface
        self.colour = border_colour
        self.outer_arc_square = outer_arc_square
        self.inner_scale_factor = 40
        self.arc_thickness = border_thickness
        self.data_scale_factor = 5
        self.reading_arc_thickness = 31
        self.band_0_limit_rpm = 2200

        # Default arc bands, pre-calculated.
        # BAND 0
        self.band_0_arc_start = (180 - (self.band_0_limit_rpm / DisplayDialGauge.data_per_degree)) * (self.PI/180)
        self.band_0_arc_end = self.PI
        # BAND 1
        self.band_1_arc_start = 0
        self.band_1_arc_end = self.band_0_arc_start

        self.inner_arc_square = [self.outer_arc_square[0]+self.inner_scale_factor,
                                 self.outer_arc_square[1]+self.inner_scale_factor,
                                 self.outer_arc_square[2]-(2*self.inner_scale_factor),
                                 self.outer_arc_square[3]-(2*self.inner_scale_factor)
                                 ]
        self.border_arcs = [self.outer_arc_square, self.inner_arc_square]

        self.reading_arc_square = [self.outer_arc_square[0]+self.data_scale_factor,
                                self.outer_arc_square[1]+self.data_scale_factor,
                                self.outer_arc_square[2]-(2*self.data_scale_factor),
                                self.outer_arc_square[3]-(2*self.data_scale_factor)
                                 ]
        self.arc_start = (7*self.PI)/4
        self.arc_end = self.PI
        self.draw_single_colour_border_arcs(self.colour)
        self.data_arc(self.data_value)

    def draw_single_colour_border_arcs(self, bcolour):
        for arc in self.border_arcs:
            pygame.draw.arc(self.surface, bcolour, (arc[0], arc[1], arc[2], arc[3]), self.arc_start, self.arc_end,
                            self.arc_thickness)

    def draw_wiper_arc(self):
        pygame.draw.arc(self.surface, BLACK, self.reading_arc_square, self.arc_start, self.arc_end,
                        self.reading_arc_thickness)

    def data_arc(self, data_value):
        # calculations are quadrant specific.
        self.data_value = data_value
        if data_value > DisplayDialGauge.horizontal_line_in_rpm:         # Over > 6160rpm which is center line on gauge.
            # 3rd quadrant calculations
            remaining_rpm = self.data_value - DisplayDialGauge.horizontal_line_in_rpm
            remaining_degrees = remaining_rpm / DisplayDialGauge.data_per_degree
            start_degrees = 360 - remaining_degrees
            start_rads = start_degrees * (self.PI / 180)
            end_rads = 0

            if data_value > ((max_rpm - DisplayDialGauge.horizontal_line_in_rpm) / 2) + \
                    DisplayDialGauge.horizontal_line_in_rpm:
                data_colour = RED

            else:
                data_colour = YELLOW

            pygame.draw.arc(self.surface, DARK_GREEN, self.reading_arc_square, self.band_0_arc_start,
                            self.band_0_arc_end, self.reading_arc_thickness)
            pygame.draw.arc(self.surface, GREEN, self.reading_arc_square, self.band_1_arc_start, self.band_1_arc_end,
                            self.reading_arc_thickness)
            # reading_arc_square is the square around the arc
            # start_rads is the radians where the arc starts
            # end_rads for 3rd quadrant is the 0 rads or 360 degs
            pygame.draw.arc(self.surface, data_colour, self.reading_arc_square, start_rads, end_rads,
                            self.reading_arc_thickness)

        else:
            # Calculate quadrant 1 and 2
            remaining_degrees = data_value / DisplayDialGauge.data_per_degree
            start_degrees = 180 - remaining_degrees
            start_rads = start_degrees * (self.PI / 180)
            if data_value > self.band_0_limit_rpm:
                # Draw full band 0
                pygame.draw.arc(self.surface, DARK_GREEN, self.reading_arc_square, self.band_0_arc_start,
                                self.band_0_arc_end, self.reading_arc_thickness)
                # Draw calculated band 1
                pygame.draw.arc(self.surface, GREEN, self.reading_arc_square, start_rads, self.band_0_arc_start,
                                self.reading_arc_thickness)
            else:
                # Draw calculated band 0
                pygame.draw.arc(self.surface, DARK_GREEN, self.reading_arc_square, start_rads,
                                self.band_0_arc_end, self.reading_arc_thickness)

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class DisplayBarGauge(object):
    """
        Bar gauge to display increasing value such as RPM.
        Designed to be used primarily as a shift light, but could be used for anything.
        Operating by printing an image and then masking with with background cover.
        The size of the mask is altered depending on the magnitude of the data value.
        Images must be of the same dimensions otherwise masking will be incorrect.

        This bar works horizontally.
    """

    def __init__(self, name, data_value, max_data_value, wsurface, image_list, mask_colour, image_xy_list, limits):

        self.name = name                                               # A arbitrary name for the object.
        self.data = data_value                                         # Data value to be plotted
        self.max_data_value = max_data_value                           # The maximum value observed in the data value
        self.windowsSurface = wsurface                                 # Target Pygame surface
        self.image_list = image_list                                   # Supplied list of images to use
        self.mask_colour = mask_colour                                 # Mask colour should always be background colour
        self.image_xy = image_xy_list                                  # Location of where to draw the rect/images
        self.limits = limits
        # Load the listed images into a list of loaded images for use.
        # Use of images would be .... self.windowsSurface.blit(self.loaded_images[2], (100, 100))
        self.loaded_images = []
        for image in self.image_list:
            self.loaded_images.append(pygame.image.load(image).convert())

        # Get size of mask rectangle based on first image mask_rect (tuple)
        self.mask_rect = self.loaded_images[0].get_rect().size

        # set static mask rectangle coordinates.
        self.mask_start_x = self.image_xy[0] + self.mask_rect[0]
        self.mask_start_y = self.image_xy[1]
        self.mask_end_y = self.mask_rect[1]

        self.updatebar(self.data)

    def updatebar(self, data):
        self.data = data
        # calculate the mask_end_x as data/max_data
        mask_end_x = 0 - (self.mask_rect[0] - ((self.data/self.max_data_value) * self.mask_rect[0]))
        # set mask rectangle coordinates
        mask_rectangle = Rect(self.mask_start_x, self.mask_start_y, mask_end_x, self.mask_end_y)
        # Set which image is displayed based on data value
        image_to_display = self.loaded_images[0]
        if self.data < self.limits[0]:
            image_to_display = self.loaded_images[0]

        if self.limits[0] < self.data < self.limits[1]:
            image_to_display = self.loaded_images[1]

        if self.limits[1] < self.data < self.limits[2]:
            image_to_display = self.loaded_images[2]

        if self.data > self.limits[2]:
            image_to_display = self.loaded_images[3]
        # Blit image
        self.windowsSurface.blit(image_to_display, self.image_xy)
        # Mask image
        pygame.draw.rect(self.windowsSurface, self.mask_colour, mask_rectangle)
        return

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class DisplayTellTale(object):
    """
    Industry standard tell-tales.

    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class SplitDataText(object):
    """
        Text class for displaying large text inside the center of a gauge.
        Use is specifically for RPM.
        The concept is to reduce the font size of the two least significant digits as they change too rapidly,
        as a result may be distracting to a driver.
        This uses a simplified text printing function without a rectangle to wipe the previous char, this works but
        requires the use of uniform fonts.

        msd = most significant digits, i.e. in rpm thousands and hundreds.
        lsd = least significant digits, i.e. in rpm tens

        Note,
            Does not currently support changing colour based on data value.

    """
    def __init__(self, name,  wsurface, font, mainfontsize, fontpercentagereduction, msd_colours, lsd_colours,
                 location):

        self.name = name
        self.windowSurface = wsurface
        self.font = font
        self.main_font_size = mainfontsize
        self.font_reduction = fontpercentagereduction
        self.msd_fore_colour = msd_colours[0]
        self.msd_back_colour = msd_colours[1]
        self.lsd_fore_colour = lsd_colours[0]
        self.lsd_back_colour = lsd_colours[1]
        self.loc_x = location[0]
        self.loc_y = location[1]
        self.data = ""                                                              # read data value
        self.msd = ""                                                               # two most significant digits
        self.lsd = ""                                                               # two least significant digits
        self.msd, self.lsd = self.split_data(self.data)                             # split the text into two parts
        self.update(self.data)

    def split_data(self, data):
        data = data.zfill(4)
        split_list = list(str(data))
        msd = split_list[0] + split_list[1]
        lsd = split_list[2] + split_list[3]
        return msd, lsd

    def update_msd(self, msd, lsd):
        rpm_Font = pygame.font.Font(self.font, self.main_font_size)
        text = rpm_Font.render(msd, True, self.msd_fore_colour, self.msd_back_colour)
        rect_around_text = text.get_rect().size
        self.windowSurface.blit(text, (self.loc_x, self.loc_y))
        # now update the remaining lsd, probably shoudn't structure the code like this, but the lsd must be done too!
        self.update_lsd(lsd, rect_around_text)
        return

    def update_lsd(self, lsd, rect_around_text):
        # smaller font calc
        smallfont = int(self.main_font_size * self.font_reduction)
        rpm_Font_small = pygame.font.Font(self.font, smallfont)
        # calc new start x, rect_x + self.loc_x etc
        small_loc_x = self.loc_x + rect_around_text[0]
        text = rpm_Font_small.render(lsd, True, self.lsd_fore_colour, self.lsd_back_colour)
        self.windowSurface.blit(text, (small_loc_x, self.loc_y))
        return

    def update(self, data):
        self.msd, self.lsd = self.split_data(str(data))
        self.update_msd(self.msd, self.lsd)
        return

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class LabelText(object):
    """
        General class for displaying text on the screen

        name = simple name
        wsurface = pygame surface
        textstr = string to display
        forecolour = foreground colour of the text string
        backcolour = background colour of the text string
        font = font to be used
        loc_x = x coord
        loc_y = y coord

    """
    def __init__(self, name, wsurface, textstr, forecolour, backcolour, font, loc_x, loc_y):
        self.name = name
        self.windowSurface = wsurface
        self.textstr = str(textstr).ljust(5, " ")
        self.forecolour = forecolour
        self.backcolour = backcolour
        self.font = font
        self.loc_x = loc_x
        self.loc_y = loc_y
        text = self.font.render(self.textstr, True, self.forecolour, self.backcolour)
        text_rect = text.get_rect()
        text_rect.centerx = self.loc_x
        text_rect.centery = self.loc_y
        # draw the text onto the surface
        self.windowSurface.blit(text, (self.loc_x, self.loc_y))



    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class DataText(LabelText):
    def __init__(self, name, wsurface, textstr, forecolour, backcolour, font, loc_x, loc_y):
        super().__init__(name, wsurface, textstr, forecolour, backcolour, font, loc_x, loc_y)


    def update(self, new_data):
        self.textstr = str(new_data).ljust(5, " ")
        text = self.font.render(self.textstr, True, self.forecolour, self.backcolour)
        text_rect = text.get_rect()
        text_rect.centerx = self.loc_x
        text_rect.centery = self.loc_y
        # draw the text onto the surface
        self.windowSurface.blit(text, (self.loc_x, self.loc_y))


