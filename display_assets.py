#! /usr/bin/env python3
#
import pygame

from colours import *
from dash_support import *
from gauges_text import *


def draw_screen_borders(windowSurface):
    middle_line = 355
    d1 = 300
    d2 = 680

    # X values
    x1 = 0
    x2 = 147

    # Y values
    y1 = 13
    y2 = 35
    y3 = 360
    y4 = display_height - y1
    # Dark lines first. which will be overwritten
    pygame.draw.line(windowSurface, DARK_GREY, (x2, y2), (x2, middle_line), 1)

    # draw table inner borders
    start_y = 60
    count = 10
    while count > 0:
        pygame.draw.line(windowSurface, DARK_GREY, (x1, start_y), (d1, start_y), 1)
        count -= 1
        start_y = start_y + 30

    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y1), (display_width, y1), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y2), (display_width, y2), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y3), (display_width, y3), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (d1, y2), (d1, y3), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (d2, y2), (d2, y3), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y4), (display_width, y4), 1)
    return


def draw_screen_labels(windowSurface, labelFont, x, y, spacing):
    for label in data_value_labels:
        LabelText(label, windowSurface, label, DARK_GREEN, TEXT_BG, labelFont, x, y)
        y += spacing
    return


def list_data_text(windowSurface, datafont, x, y, spacing):
    list_of_data_txt = []
    for value in data_value_labels:
        list_of_data_txt.append(DataText(value, windowSurface, "00000", GREEN, TEXT_BG, datafont, x, y))
        y += spacing
    return list_of_data_txt
