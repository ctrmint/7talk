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


def display_data_structure():
    print("The following structure is used;")
    for i in range(len(data_value_labels)):
        print("(" + str(i) + ", incrementing packet counter[0-10], " + str(data_value_labels[i]).ljust(20, " ")
              + ", data value)")
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
    return values


def packing(fmt, unpacked_data):
    packed_data = fmt.pack(*unpacked_data)
    return packed_data


def send_data(packed_data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating socket with these two lines
    server_address = (server_addr, server_udp_port)  # need to be in loop otherwise errors!

    try:  # try ...
        sock.connect(server_address)  # and connect to the dash server socket
        try:  # connected...
            sock.send(packed_data)  # send the packet.
        finally:
            sock.close()  # now close the socket!
            success = True

    except socket.error as msg:  # initial try to connect failed!!
        print("Couldn't connect with the server: %s." % msg)  # error and try again with while loop!
        # will print to screen failure
        success = False
    return success

def main():
    display_data_structure()                                                # Print som details regarding structure
    fmt = struct.Struct('I I 20s I')                                        # format of packing structure
    b = 0
    d = 0
    while 1:
        b += 1
        if b > 10:
            b = 0

        values = gen_data(b, d)                                     # generate some test values, needs a better function

        packed_data = packing(fmt, values)                          # pack the data to be sent via socket
        send_data(packed_data)                                      # send packed data via function.




if __name__ == '__main__':
    main()
