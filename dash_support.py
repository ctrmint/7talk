# ----------------------------------------------------------------------------------------------------------------------
# Caterham 7 Dash
# Revision  :   0.1
# Author    :   Mark Rodman
# ----------------------------------------------------------------------------------------------------------------------
# Supporting parameters for 7 Dash display
# Notes,
#   Needs to be setup via configuration file rather than importing in this manner.
#   This was a quick solution during dev
#   In the process of being retired.
# ----------------------------------------------------------------------------------------------------------------------

#Welcome string
VERSION = 0.5
version = str(VERSION)
APP_NAME = "7 Talk Dashboard."
WELCOME = "Welcome to " + APP_NAME + " Build:" + str(VERSION)

ret_count_val = 3


#CLASS STUFF
buffer_limit = 20
debug_view = False
live = False

# GENERAL DISPLAY SETTINGS
display_height = 480
display_width = 800
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
LABEL_FONTSIZE = 14
DATA_FONTSIZE =  16


#RPM Display stuff
rpm_delay = 2000
RPM_COVER_RECT_START_HEIGHT = 15
RPM_COVER_RECT_END_HEIGHT = 54

