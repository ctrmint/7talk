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

import binascii, socket, struct, sys, random, argparse, logging, csv, pprint, math, time
import mbe                                                     # coded by John Martin / PurpleMeanie, forked slightly
from dash_support import *
from dash_client_udp import *
from dash_client_support import *


def packing(fmt, unpacked_data):
    packed_data = fmt.pack(*unpacked_data)
    return packed_data


def send_data(packed_data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating socket with these two lines
    server_address = (server_addr, server_udp_port)  # need to be in loop otherwise errors!

    try:  #                                  try ...
        sock.connect(server_address)        # and connect to the dash server socket
        try:                                # connected...
            sock.send(packed_data)          # send the packet.
        finally:
            sock.close()                    # now close the socket!
            success = True                  # Unused at the moment, road map to add future functionality

    except socket.error as msg:             # initial try to connect failed!!
        print("Couldn't connect with the server: %s." % msg)                      # error and try again with while loop!
        success = False
    return success


def test_routine(fmt):                                      # test routine designed to test comms, uses random data etc.
    # needs rewriting to support the new class.
    packet_counter = 0
    while packet_counter < 10:                    # This section is a little verbose, designed to make it more readable.
        for i in range(len(data_value_labels)):
            name_string = str(data_value_labels[i]).ljust(20, " ")   # ensure the name string is 20 chars (equal length)
            a = i                                                    # historic use of a, so a becomes i.
            b = packet_counter                                       # historic use of b, packet counter is added to b
            c = bytearray(name_string.encode('utf-8'))               # historic use of c, encoded name_string
            d = random.randint(0, 130)                               # historic use of d, random val,
            values = (a, b, c, d)                                    # put the lot together, yes long winded!
            packed_data = packing(fmt, values)                       # pack the data to be sent via socket
            send_data(packed_data)                                   # send packed data via function.
        if packet_counter < 10:                                      # Increment the packet counter if < 10
            packet_counter += 1                                      # as above.
    return                                                           #  ------


def main():
    UDP_tx = True
    stdout_dict = True
    fmt = struct.Struct('I 20s I')                                            # format of packing structure for UDP
    controller = SendDataController()                                         # UDP transmission controller

    results = dict()                                                            # ISOTP results dictionary

    if mbe.test_mode:
        variables_to_follow = vars_to_follow_test_mode
    else:
        variables_to_follow = vars_to_follow_live

    parser = argparse.ArgumentParser(prog='UniHatRevs', description='Shows rev.')
    parser.add_argument('--interface', '-i', help='The can interface to open', required=True)
    parser.add_argument('--variables', '-v', help='Input MBE variables filename', required=True)
    parser.add_argument('--query_id', '-q', help='CAN query ID (default 0x0cbe1101)', default=0x0cbe1101)
    parser.add_argument('--response_id', '-r', help='CAN resdponse ID (default 0x0cbe0111', default=0x0cbe0111)
    parser.add_argument('--loglevel', '-l', help='Logging level to show',
                        choices=['INFO', 'DEBUG', 'WARNING', 'ERROR', 'NONE'], default="ERROR")
    parser.add_argument('--logfile', '-f', help='If set logging will be sent to this file')
    parser.add_argument('--version', '-V', action='version', version='%(prog)s ' + version)

    args = parser.parse_args()

    logging_level = getattr(logging, args.loglevel, None)
    logging.basicConfig(level=logging_level, filename=args.logfile, filemode='w')

    ecu = mbe.mbe()
    ret = ecu.set_options(args.variables, args.query_id, args.response_id, args.interface)

    if not ret:
        logging.error("Unable to set options")
        exit()

    logging.info("Added all the variables we expected")


    if not ret:
        logging.error("Unable to set options")
        exit()

    if ecu.add_variable_list_to_follow(variables_to_follow) != len(variables_to_follow):
        logging.warning("Ooops, didn't add all the vars I wanted to")
    else:
        logging.info("Added all the variables we expected")

    ecu.bind()


    while 1:
        # get fresh can data or not!
        if ecu.process_all_pages(results):
            logging.debug(pprint.pformat(results))
            for key in (results.keys()):                                            # set index value
                value = int((results.get(key))['value'])                            # pull value from nested dictionary
                short_desc = str((results.get(key))['short_desc']).lstrip()         # pull the short_desc from the dict
                if UDP_tx:
                    mypacket = DataPacket(fmt, short_desc, value)
                    controller.send_packet(mypacket)


            if stdout_dict:
                pp = pprint.PrettyPrinter(indent=10)
                pp.pprint(results)


            time.sleep(0.125)

        else:
            test_routine(fmt)                                               # Test routine

if __name__ == '__main__':
    main()