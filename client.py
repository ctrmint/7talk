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
# Now with json support
# ----------------------------------------------------------------------------------------------------------------------

import binascii, socket, struct, sys, random, argparse, logging, csv, pprint, math
import mbe                                                     # coded by John Martin / PurpleMeanie, forked slightly
from dash_support import *
from dash_client_udp import *
from logs import log_memory
from time import sleep, strftime, time
import json
from types import SimpleNamespace

def packing(fmt, unpacked_data):
    packed_data = fmt.pack(*unpacked_data)
    return packed_data


#def send_data(packed_data):
 #   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating socket with these two lines
  #  server_address = (server_addr, server_udp_port)  # need to be in loop otherwise errors!

   # try:                                                    # try ...
    #    sock.connect(server_address)                        # and connect to the dash server socket
     #   try:                                                # connected...
      #      sock.send(packed_data)                          # send the packet.
      #  finally:
      #      sock.close()                                    # now close the socket!
       #     success = True                                  # Unused at the moment, road map to add future functionality

    #except socket.error as msg:                             # initial try to connect failed!!
     #   print("Couldn't connect with the server: %s." % msg)                      # error and try again with while loop!
      #  success = False
    #return success


def main():
    with open('client_config.json') as json_data_file:
        cfg_vals = json.load(json_data_file)
    cfg = SimpleNamespace(**cfg_vals)

    UDP_tx = cfg.UDP_Dash['UDP_Tx']
    stdout_dict = cfg.std_out['std_out']
    logger = cfg.logs["logger"]
    time_delay = cfg.CAN["time_delay"]
    fmt = struct.Struct('I 20s I')                                                 # format of packing structure for UDP
    controller = SendDataController()                                              # UDP transmission controller

    results = dict()                                                               # ISOTP results dictionary

    if mbe.test_mode:
        variables_to_follow = (cfg.CAN["vars_test"])                               # now in json
    else:
        variables_to_follow = (cfg.CAN["vars_live"])                               # now in json

    parser = argparse.ArgumentParser(prog='UniHatRevs', description='Shows rev.')
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
    ret = ecu.set_options(cfg.CAN["variable_file"], args.query_id, args.response_id, cfg.CAN["interface"])

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

    log_handler = log_memory(cfg.logs["filename"], cfg.logs["log_line_cache"], time_delay, cfg.logs["verbose"])

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
                pp = pprint.PrettyPrinter(indent=cfg.std_out["pp_indent"])
                pp.pprint(results)

            if logger:
                log_handler.new_log(results)

            sleep(time_delay)

if __name__ == '__main__':
    main()