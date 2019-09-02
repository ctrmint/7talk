#! /usr/bin/env python3
# ---------------------------------------------------------------
# Caterham 7 Dash
# Revision  :   0.1
# Author    :   Mark Rodman
# ---------------------------------------------------------------
# Reads information from the MBE ECU for display on screen via
# pygame.
# ---------------------------------------------------------------
# Status: incomplete
# ---------------------------------------------------------------
# Notes,
# ------
# __Dictionaries__
#       data_dict = dictionary of data excluding RPM, eg TPS Site : 10. Contents initially built from data_value_labels
# __Lists__
#       data_txt_as_list = list of instances of DataText, used to print data on the screen.

import os, sys, time, datetime
import random
import can
from dash_support import *
from colours import *
from gauges_text import *
from pygame.locals import *
from candata import *
from display_assets import *


# Initial setup, needs restructuring, shouldn't be global!
# init pygame
pygame.init()
pygame.font.init()
pygame.mixer.quit()   # bug fix, killing mixer stop CPU hog!!!

# Pygame event for CANBus
POLLCAN = pygame.USEREVENT + 1
pygame.time.set_timer(POLLCAN, PollCAN_schedule)

# sort display surface
gameDisplay = pygame.display.set_mode((display_width, display_height))
windowSurface = pygame.display.set_mode((display_width, display_height), 0, 32)
pygame.display.set_caption(display_title)
windowSurface.fill(STARTCOLOUR)

# setup fonts
available_fonts = pygame.font.get_fonts()
for font in range(len(available_fonts)):
    if available_fonts[font] == LCD_font:
        lcd_fontpath = pygame.font.match_font(available_fonts[font])
    if available_fonts[font] == 'hack':
        hack_font = pygame.font.match_font(available_fonts[font])

# set up fonts
rpmFont = pygame.font.Font(hack_font, rpm_fontsize)
labelFont = pygame.font.Font(hack_font, label_fontsize)
dataFont = pygame.font.Font(hack_font, data_fontsize)
# setup clock
clock = pygame.time.Clock()
# ------------------------------------------------------------------


def demo_rpm(demo_rpm_val):
    if demo_rpm_val < max_rpm:
        demo_rpm_val += 25
    else:
        demo_rpm_val = 0
    return demo_rpm_val


def processing_loop(bus):
    table_collect = table_collect_start
    # setup screen layout, borders etc
    draw_screen_borders(windowSurface)
    draw_screen_labels(windowSurface, labelFont, 3, 40, 30)
    data_txt_as_list = list_data_text(windowSurface, dataFont, 160, 40, 30)

    # declare rpm txt instance and display 0000 value
    rpm_txt = SplitDataText("rpm", windowSurface, hack_font, rpm_fontsize, 0.9, ([GREEN, TEXT_BG]),
                            ([V_DARK_GREEN, TEXT_BG]), [420, 160])

    # declare rpm gauge instance and display bar for zero value
    rpm_bar = DisplayBarGauge("test", 0, max_rpm, windowSurface,
                              ([rev_image1, rev_image2, rev_image3, rev_image_shift]),
                              BLACK, ([10, 15]), ([2500, 6600, 7500]))

    rpm_dial_gauge = DisplayDialGauge(windowSurface, [330, 55, 325, 325], 2, GAUGE_BORDER_COLOUR)

    trace_gauge = DisplayTraceGauge(windowSurface, ([0, 365]), 100, ([DARK_GREEN, BLACK]), (7800, 0), False, True)

    # create data dictionary
    data_dict = dict.fromkeys(data_value_labels, 0)

    keep_running = True
    demo_loop = False
    random_loop = False
    demo_rpm_val = 0
    rpm_reading = Rpmval("rpm", 0)

    while keep_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False
                pygame.quit()
                sys.exit()
            elif event.type == POLLCAN:
                if demo_loop:
                    demo_rpm_val = demo_rpm(demo_rpm_val)
                    rpm_reading.set_change(demo_rpm_val)
                if random_loop:
                    rpm_reading.set_change(random.randint(1, max_rpm))

                else:
                    if live:                           # collect RPM Data via can at base frequency set by pygame clock
                        rough_str, hex_id, data_hex = receive_can_frame(bus)
                        rpm_value = process_can_message(rough_str)
                        rpm_reading.set_change(rpm_value)

                        if table_collect == 0:                                  # collect table data, at lower frequency
                            # poll for table data from CAN here.                                    # collect goes here
                            table_collect = table_collect_start                   # reset timer used to lower frequency
                        table_collect -= 1
                    else:                                                            # testing loop used to display data
                        if table_collect == 0:                                           # again check frequency counter
                            data_dict['TPS Site'] = (random.randint(1, 16))                     # test update, TPS Site
                            data_dict['Air Temp'] = (random.randint(1, 30))                      # test update, Air Temp
                            data_dict['Coolant Temp'] = (random.randint(1, 110))             # test update, Coolant Temp
                            data_dict['Battery Volt'] = (round(random.uniform(1, 13), 2))    # test update, Battery Volt
                            data_dict['Throttle Angle'] = (round(random.uniform(1, 5.00), 3))
                            table_collect = table_collect_start                                     #  reset the counter
                        table_collect -= 1                                                            #  dec the counter

            elif event.type == KEYDOWN:
                demo_loop = False
                random_loop = False
                if event.key == K_UP:
                    rpm_reading.test_change(250)
                if event.key == K_DOWN:
                    rpm_reading.test_change(-100)
                if event.key == K_LEFT:
                    rpm_reading.reset_current_val(0)
                if event.key == K_RIGHT:
                    rpm_reading.wipe()
                if event.key == K_LSHIFT:
                    demo_loop = True
                if event.key == K_RSHIFT:
                    random_loop = True

            if not rpm_reading.rx_val_inc:
                rpm_dial_gauge.draw_wiper_arc()

            # bug fix to stop zero values from the keyboard.  -- code improvement needed
            if rpm_reading.rx_val < 0:
                rpm_reading.rx_val = 0

            rpm_bar.updatebar(rpm_reading.rx_val)
            rpm_dial_gauge.data_arc(rpm_reading.rx_val)
            rpm_txt.update(rpm_reading.rx_val)
            trace_gauge.update(rpm_reading.rx_val)

            # update main data table text values from  -----
            for data in (data_dict.items()):
                for i in range(len(data_txt_as_list)):
                    if data_txt_as_list[i].name == data[0]:   # match name of dict item with instance name! and if match
                       data_txt_as_list[i].update(data[1])    # update instance data, to update screen etc.
            # ---------------------------------------------

        pygame.display.update()
        clock.tick(clock_val)
    return


def main():
    if not live:
        bus = ''
    else:
        bus = can.interface.Bus(bustype=bustype, channel=mybus, bitrate=bitrate)
    processing_loop(bus)
    return


if __name__ == '__main__':
    main()
