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
    # needs rewriting to support the new class.
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

    if mbe.test_mode:
        variables_to_follow = [
            #'RT_ENGINESPEED',
            'RT_AIRTEMP1(LIM)',
            'RT_COOLANTTEMP1(LIM)',
            #'RT_BATTERYVOLTAGE(LIM)',
            'RT_SOFTCUTTIME',
            #'RT_HARDCUTTIME'
        ]
    else:
        variables_to_follow = [
            #    	'RT_THROTTLESITE1',
            #    	'RT_BATTERYVOLTAGECOMP',
            #    	'RT_IGNITIONADVANCEBANK1',
            #    	'RT_TPSVSSPEEDIGN+TRIM1',
            #    	'RT_INJECTIONTIMEA',
            #    	'RT_COOLANTTEMP1(LIM)',
        #'RT_AIRTEMP1(LIM)',
            #    	'RT_MAPPINGPOT1LIM',
            #    	'RT_MAPPINGPOT2LIM',
            #    	'RT_COOLANTFUELFACTOR',
        #'RT_BATTERYVOLTAGE(LIM)',
            #    	'RT_AIRTEMPFUELFACTOR',
            #    	'RT_DUTYCYCLEA',
            #    	'RT_TPSFUEL+TRIMBANK1',
        #'RT_SOFTCUTTIME',
        #'RT_HARDCUTTIME',
            #    	'RT_THROTTLEANGLE1(RAW)',
            #    	'RT_ENGINERUNTIME',
            ##   	 'RT_ECUSTATUS',
            #    	'RT_BAROSCALEDLIM',
            #    	'RT_THROTTLEANGLEINCREASING',
            #    	'RT_BAROFUELCOMP',
            #    	'RT_CRANKCOUNT',
        #'RT_ENGINESPEED'
        ]
    display_data_structure()                                                    # Print som details regarding structure
    just_testing = False
    fmt = struct.Struct('I I 20s I')                                            # format of packing structure
    controller = SendDataController()                                           # transmission controller

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
    results = dict()

    while 1:
        if not just_testing:
            #i = 1
            #mypacket = DataPacket(fmt, i, data_value_labels[i], 60 )
            #controller.send_packet(mypacket)

            if ecu.process_all_pages(results) != False:
                logging.debug(pprint.pformat(results))
                #unicorn_revs(results['RT_ENGINE_SPEED'])

            time.sleep(0.25)
        else:
            test_routine(fmt)                                               # Test routine

if __name__ == '__main__':
    main()
