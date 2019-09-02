# -----------------------------------------
# Supporting parameters for 7 Dash display
#
# Notes,
#   Needs to be setup via configuration file rather than importing in this manner.  This was a quick solution during dev
#
# -------------
mybus = 'vcan0'
bitrate = 500000
bustype= 'socketcan'
ret_count_val = 3
#Event timers
PollCAN_schedule = 10 # milliseconds
table_collect_start = 30
#CLOCK
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

# FONT NAMES
LCD_font = "open24displayst"
# FONT Size
default_fontsize = 30
rpm_fontsize = 70
label_fontsize = 12
data_fontsize = 14

# Display Labels & Locations.--------------------
# Throttle Angle, Air Temp, Coolant Temp, Coolant fuel factor, Air Temp fuel factor, Throttle Angle Increasing,
# TPS Fuel + Trim, TPS Speed Ignition + Trim, TPS Site, Battery Voltage, Battery Voltage compensation

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
#KNOWN RESPONSES
known_response = {"RPM" : ["03.81.00.00.00.00.f8.7c"]}