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
host = 'localhost'
udp_port = 11111

# Packing structure
#unpacker = struct.Struct('I I 20s I')

#CAN / ISOTP COMMS PARAMETERS
mybus = 'vcan0'
bitrate = 500000
bustype= 'socketcan'
Rxid = 0x0cbe0111
Txid = 0x0cbe1101
ret_count_val = 3

#EVENT TIMERS AND PYGAME CLOCK
PollCAN_schedule = 10 # milliseconds
table_collect_start = 30
clock_val = 60

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
rpm_fontsize = 70
label_fontsize = 12
data_fontsize = 14

# Display Labels & Locations.--------------------
data_value_labels = ["Throttle Angle", "Air Temp", "Coolant Temp", "Coolant fuel factor", "Air Temp fuel factor",
                     "Throttle Angle Inc", "TPS Fuel+Trim", "TPS Speed Ign+Trim", "TPS Site",
                     "Battery Volt", "Battery Volt comp"]

#RPM Display stuff
max_rpm = 7700
rpm_delay = 2000
rev_image1 = 'assets/shiftbar/rev1.jpg'
rev_image2 = 'assets/shiftbar/rev2.jpg'
rev_image3 = 'assets/shiftbar/rev3.jpg'
rev_image_shift = 'assets/shiftbar/shift.jpg'
RPM_COVER_RECT_START_HEIGHT = 15
RPM_COVER_RECT_END_HEIGHT = 54

#KNOWN REQUESTS

Serial_number = bytearray(b'\x04\x00\x0d')

#KNOWN RESPONSES
known_response = {"RPM" : ["03.81.00.00.00.00.f8.7c"]}

#30:31  = Throttle Angle 1 Raw, in Volts, 0V min, 5V max, 0.0000762951V per bit
#36:37  = Air Temperature
#44:45  = Coolant Temperature
#4c:4d  = Coolant fuel factor
#4e:4f  = Air Temperature fuel factor
#50:51  = Throttle Angle Increasing, in Volts, 0V min, 5V max, 0.0000762951V per bit
#5a:5b  = TPS Fuel + Trim
#5c:5d  = TPS Speed Ignition +Trim
#64     = TPS Site
#6a:6b  = Baro Pressure
#7c:7d  = Engine Speed
#9e:9f  = Battery Voltage
#a0:a1  = Battery Voltage compensation
#d8:d9  = Mapping Pot 1 Limit, in Percent, -100% min, 100% max, 0.0030518% per bit
#da:db  = Mapping Pot 2 Limit, in Percent, -100% min, 100% max, 0.0030518% per bit

