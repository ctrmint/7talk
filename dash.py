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

import random, struct, json, socket
#from dash_support import *
#from colours import *
from gauges_text import *
from pygame.locals import *
from candata import *
from types import SimpleNamespace


def pygame_setup(cfg):
    pygame.init()  # Init pygame
    pygame.font.init()  # Init pygame fonts
    pygame.mixer.quit()  # BUG FIX, Quitting mixer stops it from hogging cpu!!!

    POLLCAN = pygame.USEREVENT + 1  # Pygame event for CANBus
    pygame.time.set_timer(POLLCAN, cfg.Timers['PollCAN_schedule'])  # weird still required!
    clock = pygame.time.Clock()  # Setup PG clock, critical component to runtime.

    # sort display surface
    gameDisplay = pygame.display.set_mode((cfg.Display['width'], cfg.Display['height']))
    windowSurface = pygame.display.set_mode((cfg.Display['width'], cfg.Display['height']), 0, 32)
    pygame.display.set_caption(display_title)
    windowSurface.fill(STARTCOLOUR)

    # setup fonts
    available_fonts = pygame.font.get_fonts()
    for font in range(len(available_fonts)):
        if available_fonts[font] == LCD_font:
            lcd_fontpath = pygame.font.match_font(available_fonts[font])
        if available_fonts[font] == 'hack':
            hack_font = pygame.font.match_font(available_fonts[font])
            rpmFont = pygame.font.Font(hack_font, RPM_FONTSIZE)
            labelFont = pygame.font.Font(hack_font, LABEL_FONTSIZE)
            dataFont = pygame.font.Font(hack_font, DATA_FONTSIZE)
        else:
            if available_fonts[font] == 'freemono':
                hack_font = pygame.font.match_font(available_fonts[font])
                rpmFont = pygame.font.Font(hack_font, RPM_FONTSIZE)
                labelFont = pygame.font.Font(hack_font, LABEL_FONTSIZE)
                dataFont = pygame.font.Font(hack_font, DATA_FONTSIZE)

    return hack_font, rpmFont, labelFont, dataFont, gameDisplay, windowSurface, clock


def demo_rpm(demo_rpm_val, max_rpm):
    if demo_rpm_val < max_rpm:
        demo_rpm_val += 25
    else:
        demo_rpm_val = 0
    return demo_rpm_val


def draw_screen_borders(windowSurface):
    middle_line = 355
    d1 = 300
    d2 = 680

    # X values
    x1 = 0
    x2 = 205

    # Y values
    y1 = 13
    y2 = 35
    y3 = 360
    y4 = display_height - y1
    # Dark lines first. which will be overwritten
    pygame.draw.line(windowSurface, TABLE_CELL_COL, (x2, y2), (x2, middle_line), 1)

    # draw table inner borders
    start_y = 60
    count = 10
    while count > 0:
        pygame.draw.line(windowSurface, TABLE_CELL_COL, (x1, start_y), (d1, start_y), 1)
        count -= 1
        start_y = start_y + 30

    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y1), (display_width, y1), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y2), (display_width, y2), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y3), (display_width, y3), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (d1, y2), (d1, y3), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (d2, y2), (d2, y3), 1)
    pygame.draw.line(windowSurface, MAIN_BORDER_COLOUR, (x1, y4), (display_width, y4), 1)
    return


def processing_loop(sock, cfg):
    hack_font, rpmFont, labelFont, dataFont, gameDisplay, windowSurface, clock = pygame_setup(cfg)

    unpacker = struct.Struct(cfg.UDP_Dash['fmt_struct'])

    # Control parameters
    pending_data = True
    keep_running = True  # ensures continued operation, set false in flow to stop
    demo_loop = False  # runs demo data, set through keyboard
    random_loop = False  # runs random data, set through keyboard
    demo_rpm_val = 0  # initial value for demo data.

    # setup screen layout, borders etc
    draw_screen_borders(windowSurface)

    # declare rpm txt instance and display 0000 value
    rpm_txt = SplitDataText("rpm", windowSurface, hack_font, RPM_FONTSIZE, 0.9, ([RPM_MSB_TXT, TEXT_BG]),
                            ([RPM_LSB_TXT, TEXT_BG]), [420, 160])

    # declare rpm gauge instance and display bar for zero value
    rpm_bar = DisplayBarGauge("rpm", 0, (cfg.RPM['shift_bar_lower_rpm'], cfg.RPM['max_rpm']), windowSurface,
                              ([cfg.Images['rev_image1'], cfg.Images['rev_image2'], cfg.Images['rev_image1'],
                                cfg.Images['rev_image_shift']]), GEN_BACKGROUND, ([10, 15]),
                              (cfg.RPM['band1'], cfg.RPM['band2'], cfg.RPM['band3']))

    rpm_dial_gauge = DisplayDialGauge(windowSurface, [330, 55, 325, 325], 2,
                                      ([GAUGE_BORDER_COLOUR, DIAL_GAUGE_WIPE_COL]), cfg.RPM['max_rpm'])

    trace_gauge = DisplayTraceGauge(windowSurface, ([0, 365]), 100,
                                    ([TRACE_LINE_COL, SCROLL_WIPE_COL, TRACE_PEAK_COL]), (cfg.RPM['max_rpm'], 0),
                                    False, True)

    #  ---------------------------------------------------------    __ Display related lists __
    reference_display_table_labels = []  # Simple reference lookup table, easy check to
    # see if the table has been seen before.
    display_table_labels = []  # List of label objects from class.
    display_table_readings = []  # List of text objects relating to the data displayed
    # ----------------------------------------------------------------------------------------------------------------
    data_points = []  # List of Can_vals per value type received.  List
    # attributes are updated to reflect each new packet

    rpm_reading = Rpmval("rpm", 0)  # Instantiate  RPM reading (Can_val) object.
    # RPM operates at a higher frequency and as a result has been separated for ease.

    while keep_running:  # Now start core loop used during reception.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    pygame.quit()
                    sys.exit()
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
                    rpm_reading.wipe()  # needs to fixed!!!!!
                if event.key == K_LSHIFT:
                    random_loop = False
                    demo_loop = True
                if event.key == K_RSHIFT:
                    demo_loop = False
                    random_loop = True

            if not rpm_reading.rx_val_inc:
                rpm_dial_gauge.draw_wiper_arc()

            if demo_loop:
                rpm_reading.rx_val = demo_rpm(rpm_reading.rx_val, cfg.RPM['max_rpm'])

            if random_loop:
                rpm_reading.rx_val = random.randint(1, cfg.RPM['max_rpm'])

            # bug fix to stop zero values from the keyboard.  -- code improvement needed
            if rpm_reading.rx_val < 0:
                rpm_reading.rx_val = 0

            rpm_bar.updatebar(rpm_reading.rx_val)
            rpm_dial_gauge.data_arc(rpm_reading.rx_val)
            rpm_txt.update(rpm_reading.rx_val)
            trace_gauge.update(rpm_reading.rx_val)

        clock.tick(cfg.Timers['Clock_value'])

        pygame.display.update()
        while pending_data:
            connection, client_address = sock.accept()

            try:
                data = connection.recv(unpacker.size)
                unpacked_data = unpacker.unpack(data)
                pending_data = False

            finally:
                connection.close()

        pending_data = True
        sock.listen()

        data_label = str(unpacked_data[1].decode("utf-8")).rstrip()
        data_value = int(unpacked_data[2])

        if data_label == "Engine Speed":  # is data engine speed, if so
            rpm_reading.set_change(unpacked_data[2])  # update dedicated engine speed

        else:
            # if len(reference_display_table_labels) < 10:
            # Capture the labels from the stream of data
            if data_label not in reference_display_table_labels:  # if not in list

                # create the labels here for each value here.
                reference_display_table_labels.append(data_label)  # add to list.
                x = cfg.Tables['table_start_x']
                y = cfg.Tables['table_start_y'] + (len(reference_display_table_labels) * cfg.Tables['table_inc_y'])
                display_table_labels.append(LabelText(data_label, windowSurface, data_label,
                                                      DARK_GREEN, TEXT_BG, labelFont, x, y))

                # repeat similar process here, for the data values.
                display_table_readings.append(DataText(data_label, windowSurface, data_value, GREEN, TEXT_BG,
                                                       dataFont, (x + cfg.Tables['table_value_offset']), y))

                data_points.append(Can_val(data_label, data_value))  # instantiate instance of class for new data label

            # we have a full list of labels and prior data, so we need to update the screen value with the current
            # data value

            for item in display_table_readings:  # run through display table readings and look for
                if item.name == data_label:  # instance name matching current data
                    item.update(data_value)  # if match update the screen label.

            for item in data_points:  # add new data point to appropriate Can_val instance in list
                if item.name == data_label:
                    item.set_change(data_value)
        pygame.display.update()  # Update the Pygame display.
    return


def main():
    with open('server_cfg.txt') as json_data_file:  # Open configuration file
        cfg_values = json.load(json_data_file)  # load json data
    cfg = SimpleNamespace(**cfg_values)  # namespace object from json

    print(cfg.App['name'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create server socket
    svr_addr = (cfg.UDP_Dash['host'], cfg.UDP_Dash['port'])  # bind socket to port
    try:
        sock.bind(svr_addr)
        print(str(sock))
        sock.listen(1)
    except:
        print("Oops - Something went wrong")
    if sock:
        processing_loop(sock, cfg)


if __name__ == '__main__':
    main()
