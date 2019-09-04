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


class DataPacket(object):
    def __init__(self, fmt, msg_type, msg_label, msg_value):
        self.counter = 0
        self.fmt = fmt
        self.msg_type = msg_type
        self.msg_label = bytearray(str(msg_label).ljust(20, " ").encode('utf-8'))
        self.msg_value = msg_value
        self.value = (self.msg_type, self.counter, self.msg_label, self.msg_value)
        self.packed_msg = self.fmt.pack(*self.value)

    def send(self):
        value = (self.msg_type, self.counter, self.msg_label, self.msg_value)
        packed_msg = self.fmt.pack(*value)
        self.transmit(packed_msg)

    def transmit(self, payload):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creating socket with these two lines
        server_address = (server_addr, server_udp_port)                          # need to be in loop otherwise errors!

        try:                                                                     # try ...
            sock.connect(server_address)                                         # and connect to the dash server socket
            try:                                                                 # connected...
                sock.send(payload)                                               # send the packet.
            finally:
                sock.close()                                                     # now close the socket!

        except socket.error as msg:                                              # initial try to connect failed!!
            print("Couldn't connect with the server: %s." % msg)                 # error and try again with while loop!

        return

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class SendDataController(object):                          # Pretty basic at the moment, just manages the packet counter
    def __init__(self, counter_dict = {}):                     # @ instantiation set up a tracking dictionary
        self.counter_dict = counter_dict                       # This will track instances of each msg type
                                                               # handy for tracking message loss etc.
    def send_packet(self, packet):
        if packet.msg_type not in self.counter_dict:           # has msg_type (index) been seen before and added to dict
            self.counter_dict.update({packet.msg_type: 0})     # Nope, so add a kv pair to dictionary for msg type index

        current_val = self.counter_dict[packet.msg_type]       # Now inc kv pair to illustrate first msg
        new_val = current_val + 1                              # or 2nd, 3rd and so on.
        if new_val > PACKET_COUNTER_LIMIT : new_val = 0
        self.counter_dict[packet.msg_type] = new_val           # this probably wants to be more efficient!

        packet.counter = new_val                               # now set counter in the packet.
        packet.send()

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


def display_data_structure():
    print("The following structure is used;")
    for i in range(len(data_value_labels)):
        print("(" + str(i) + ", incrementing packet counter[0-10], " + str(data_value_labels[i]).ljust(20, " ")
              + ", data value)")
    return

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
        success = False
    return success


def test_routine(fmt):                                      # test routine designed to test comms, uses random data etc.
    packet_counter = 0
    while packet_counter < 10:
        for i in range(len(data_value_labels)):
            name_string = str(data_value_labels[i]).ljust(20, " ")
            a = i
            b = packet_counter
            c = bytearray(name_string.encode('utf-8'))
            d = random.randint(0, 130)
            values = (a, b, c, d)
            packed_data = packing(fmt, values)  # pack the data to be sent via socket
            send_data(packed_data)  # send packed data via function.
        if packet_counter < 10:
            packet_counter += 1
    return


def main():
    display_data_structure()                                                    # Print som details regarding structure
    just_testing = False
    fmt = struct.Struct('I I 20s I')                                            # format of packing structure
    controller = SendDataController()                                           # transmission controller

    while 1:
        if not just_testing:
            i = 3
            mypacket = DataPacket(fmt, i, data_value_labels[i], 60 )
            controller.send_packet(mypacket)
        else:
            test_routine(fmt)                                               # Test routine

if __name__ == '__main__':
    main()
