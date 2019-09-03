#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------------------------------------
# Caterham 7 Dash
# Revision  :   0.1
# Author    :   Mark Rodman
# ----------------------------------------------------------------------------------------------------------------------
# Dashboard display of MBE ECU data, show support other ECUs in due course.
# Application has been built to be independent of the data source.
# Data to be displayed is received via a UDP stream, making dash.py essentially the server.
# A client needs to be executed to transmit received / decode CAN ISOTP frames from an ECU.
# Client sends one data value per UDP packet.
# ----------------------------------------------------------------------------------------------------------------------
# Status: incomplete
# ----------------------------------------------------------------------------------------------------------------------
# Notes,
# ------
# __Dictionaries__
#       data_dict = dictionary of data excluding RPM, eg TPS Site : 10. Contents initially built from data_value_labels
# __Lists__
#       data_txt_as_list = list of instances of DataText, used to print data on the screen.
# ----------------------------------------------------------------------------------------------------------------------

import os, sys, time, datetime, socket, random, binascii, struct
import can
from can.interfaces.socketcan import SocketcanBus
import isotp
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
        rpmFont = pygame.font.Font(hack_font, rpm_fontsize)
        labelFont = pygame.font.Font(hack_font, label_fontsize)
        dataFont = pygame.font.Font(hack_font, data_fontsize)
    else:
        if available_fonts[font] == 'freemono':
            hack_font = pygame.font.match_font(available_fonts[font])
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


def processing_loop(sock):
    unpacker = struct.Struct('I I 20s I')

    # Control parameters
    pending_data = True
    keep_running = True                                         # ensures continued operation, set false in flow to stop
    demo_loop = False                                           # runs demo data, set through keyboard
    random_loop = False                                         # runs random data, set through keyboard
    demo_rpm_val = 0                                            # initial value for demo data.

    table_collect = table_collect_start                         # set counter(frequency) to fetch table data
                                                                # freq = table_collect/pygame clock

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


    data_readings = []                                                 # Data storage list
    for item in data_value_labels:                                     # loop creating instances of Can_val
        data_readings.append(Can_val(item, 0))                         # based on supplied labels from data_value_labels

    rpm_reading = Rpmval("rpm", 0)                                     # Instantiate  RPM reading (Can_val) object

    while keep_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    demo_loop = False
                    random_loop = False
                    rpm_reading.test_change(250)
                if event.key == K_DOWN:
                    random_loop = False
                    demo_loop = False
                    rpm_reading.test_change(-100)
                if event.key == K_LEFT:
                    random_loop = False
                    demo_loop = False
                    rpm_reading.reset_current_val(0)
                if event.key == K_RIGHT:
                    random_loop = False
                    demo_loop = False
                    rpm_reading.wipe()    #needs to fixed!!!!!
                if event.key == K_LSHIFT:
                    random_loop = False
                    demo_loop = True
                if event.key == K_RSHIFT:
                    demo_loop = False
                    random_loop = True

            if not rpm_reading.rx_val_inc:
                rpm_dial_gauge.draw_wiper_arc()

            if demo_loop:
                rpm_reading.rx_val = demo_rpm(rpm_reading.rx_val)

            if random_loop:
                rpm_reading.rx_val = random.randint(1, 7700)


            # bug fix to stop zero values from the keyboard.  -- code improvement needed
            if rpm_reading.rx_val < 0:
                rpm_reading.rx_val = 0

            rpm_bar.updatebar(rpm_reading.rx_val)
            rpm_dial_gauge.data_arc(rpm_reading.rx_val)
            rpm_txt.update(rpm_reading.rx_val)
            trace_gauge.update(rpm_reading.rx_val)

        clock.tick(clock_val)
        pygame.display.update()
        while pending_data:
            connection, client_address = sock.accept()
            try:
                data = connection.recv(unpacker.size)
                unpacked_data = unpacker.unpack(data)
                print(str(unpacked_data) + " " + str(type(unpacked_data)))
                pending_data = False
            finally:
                connection.close()
        pending_data = True
        sock.listen()

        if unpacked_data[0] == 99:                                                         # 99 is currently id for RPM
            rpm_reading.set_change(unpacked_data[3])
        else:
            data_readings[(unpacked_data[0])].set_change(unpacked_data[3])
            data_txt_as_list[(unpacked_data[0])].update(data_readings[(unpacked_data[0])].rx_val)

        pygame.display.update()
    return

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                      # create server socket
    svr_addr = (server_addr, server_udp_port)                                                      # bind socket to port
    try:
        sock.bind(svr_addr)
        print(str(sock))
        sock.listen(1)
    except:
        print("Something went wrong")
    if sock:
        processing_loop(sock)

if __name__ == '__main__':
    main()
