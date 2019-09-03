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


def main():
    host = 'localhost'
    udp_port = 11111
    fmt = struct.Struct('I I 20s I')
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', udp_port)

    b = 0
    d = 0
    display_data_structure()
    while 1:
        b += 1
        if b > 10:
            b = 0
        values = gen_data(b, d)
        packed_data = fmt.pack(*values)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (server_addr, server_udp_port)
        try:                                                                # try ...
            sock.connect(server_address)                                    #    and connect to the dash server socket
            try:                                                            # connected...
                sock.send(packed_data)                                      #    send the packet.
            finally:
                sock.close()                                                # now close the socket!

        except socket.error as msg:                                         # initial try to connect failed!!
            print("Couldn't connect with the server: %s." % msg)            # error and try again with while loop!
                                                                            # will print to screen failure

if __name__ == '__main__':
    main()
