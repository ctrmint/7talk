# ----------------------------------------------------------------------------------------------------------------------
# Caterham 7 Dash
# Revision  :   0.1
# Author    :   Mark Rodman
# ----------------------------------------------------------------------------------------------------------------------
# Supporting parameters for 7 Dash display
#
# Notes,
#   Needs to be setup via configuration file rather than importing in this manner.  This was a quick solution during dev
# ----------------------------------------------------------------------------------------------------------------------

#UDP Listener
server_addr = 'localhost'
client_addr = server_addr
server_udp_port = 61616
PACKET_COUNTER_LIMIT = 999

# Packing structure
#unpacker = struct.Struct('I I 20s I')

#CAN / ISOTP COMMS PARAMETERS
mybus = 'vcan0'
bitrate = 500000
bustype= 'socketcan'
Rxid = 0x0cbe0111
Txid = 0x0cbe1101
ret_count_val = 3

version = "0.1"

#EVENT TIMERS AND PYGAME CLOCK
PollCAN_schedule = 1 # milliseconds
CLOCK_VAL = 60

#CLASS STUFF
buffer_limit = 20
debug_view = False
live = False

# GENERAL DISPLAY SETTINGS
display_width = 800
display_height = 480
display_title = 'Caterham Super 7 MBE Dashboard'
display_line_width = 2
line_width = 2

# SECTIONS
title_start_X = 0
title_start_Y = 35
title_end_X = display_width
title_end_Y = title_start_Y

# FONT NAMES AND SIZES
LCD_font = "open24displayst"
default_fontsize = 30
RPM_FONTSIZE = 70
LABEL_FONTSIZE = 12
DATA_FONTSIZE = 14

# Display Labels & Locations.--------------------
data_value_labels = [
                    "Throttle Angle",
                     "Air Temp",
                     "Coolant Temp",
                     "Coolant fuel factor",
                     "Air Temp fuel factor",
                     "Throttle Angle Inc",
                     "TPS Fuel+Trim",
                     "TPS Speed Ign+Trim",
                     "TPS Site",
                     "Battery Volt",
                     "Battery Volt comp"
                     ]

#RPM Display stuff
max_rpm = 7700
rpm_delay = 2000
rev_image1 = 'assets/shiftbar/rev1.jpg'
rev_image2 = 'assets/shiftbar/rev2.jpg'
rev_image3 = 'assets/shiftbar/rev3.jpg'
rev_image_shift = 'assets/shiftbar/shift.jpg'
RPM_COVER_RECT_START_HEIGHT = 15
RPM_COVER_RECT_END_HEIGHT = 54

