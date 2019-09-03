# Caterham-Dashboard

Caterham 7 MBE ECU dashboard written using Python 3.7 and Pygame 1.9.7.
It is expected to run on most Linux distributions, with the predominant target distro being Raspbian running on a Pi3.
Screen real-estate is set to 800x480, matching a commonly available Pi HDMI display.

_Design_

The dashboard is split into two core components, Dash or display (server) and a client.  The Dash is a responsible for
the visualisation of all data using Pygame, along with basic logging of the data received.

The client communicates with the ECU extracting data over the CAN bus, and then forwards to the Dash.
The client uses UDP to transmit data at the Dash.

Dash(server) and client can exist on separate hosts so long as an IP network exists between the two.7

