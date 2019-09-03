#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------------------------------------
# Caterham 7 Dash
# Revision  :   0.1
# Author    :   Mark Rodman
# ----------------------------------------------------------------------------------------------------------------------
# Description
# Client.py is a test client for the Dash.py core pygame code.
# Client sends UDP packets to dash.py for display.
# Client can be used to test the function of dash.py
# ----------------------------------------------------------------------------------------------------------------------

import binascii, socket, struct, sys, random
from dash_support import *

host = 'localhost'
udp_port = 11111
fmt = struct.Struct('I I 20s I')


def display_data_structure():
    print("The following structure is used;")
    for i in range(len(data_value_labels)):
        print("(" + str(i) + ", inc counter[0-10], " + str(data_value_labels[i]).ljust(20, " ") + ", data value)")
    return

def gen_data(b, d):
    # message format
    # i = list element
    # i = message sequence counter 0-9
    # b = message name ljust(20)
    # I = value
    # test value
    a = 6
    mystring = 'Coolant Temp'.ljust(20, " ")
    c = bytearray(mystring.encode('utf-8'))
    d = random.randint(0, 130)
    values = (a, b, c, d)
    print(str(values))
    return values

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', udp_port)


b =0
d = 0
display_data_structure()
while 1:
    b += 1
    if b > 10:
        b = 0
    values = gen_data(b, d)
    packed_data = fmt.pack(*values)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', udp_port)
    sock.connect(server_address)
    try:
        # Send data
        sock.send(packed_data)

    finally:
        sock.close()
