#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------------------------------------
# Caterham 7 Dash Client
# Revision  :   1.0
# Author    :   Mark Rodman
# ----------------------------------------------------------------------------------------------------------------------
# Description
# Client.py is a test client for the Dash.py core pygame code.
# Client sends UDP packets to dash.py for display.
# Client can be used to test the function of dash.py
# Now with json support
#    JSON file does not support comments, JSON file comments below (indented)
#           OPTIONS for 'mbe_class_log_level' = 'INFO', 'DEBUG', 'WARNING', 'ERROR', 'NONE', recommend ERROR
#
# ----------------------------------------------------------------------------------------------------------------------

import binascii, struct, sys, argparse, logging, csv, pprint, math
import mbe                                                     # coded by John Martin / PurpleMeanie, forked slightly
from dash_support import *
from dash_client_udp_broadcast import *
from logs import log_memory
from time import sleep
import json
from types import SimpleNamespace


def main():
    with open('client_cfg.txt') as json_data_file:                            # Open configuration file
        cfg_vals = json.load(json_data_file)                                  # load json data
    cfg = SimpleNamespace(**cfg_vals)                                         # namespace object from json

    # Allocate some of the cfg vals to local vars now.
    UDP_tx = cfg.UDP_Dash['UDP_Tx']                                           # Boolean, whether to transmit to dash
    stdout_dict = cfg.std_out['std_out']                                      # Boolean, write to std_out
    logger = cfg.logs["logger"]                                               # Boolean, write client logs, not mbe logs

    time_delay = cfg.CAN['time_delay']                                        # CAN query sleep timer.

    fmt = struct.Struct(cfg.UDP_Dash['fmt_struct'])                                # format of packing structure for UDP
    controller = SendDataController()                                              # UDP transmission controller

    results = dict()                                                               # ISOTP results dictionary

    if mbe.test_mode:
        variables_to_follow = (cfg.CAN["vars_test"])                               # now in json
    else:
        variables_to_follow = (cfg.CAN["vars_live"])                               # now in json

    parser = argparse.ArgumentParser(prog=cfg.App["usage"], description=cfg.App["desc"])
    parser.add_argument('--version', '-V', action='version', version='%(prog)s ' + version)
    args = parser.parse_args()

    logging_level = getattr(logging, cfg.CAN["mbe_class_log_level"], None)
    logging.basicConfig(level=logging_level, filename=cfg.CAN["mbe_class_log_file"], filemode='w')

    ecu = mbe.mbe()
    ret = ecu.set_options(cfg.CAN["variable_file"], (int(cfg.CAN["query_id"], 16)), (int(cfg.CAN["response_id"], 16)),
                          cfg.CAN["interface"])

    if not ret:
        logging.error("Unable to set options")
        exit()

    logging.info("Added all the variables we expected")

    if not ret:
        logging.error("Unable to set options")
        exit()

    if ecu.add_variable_list_to_follow(variables_to_follow) != len(variables_to_follow):
        logging.warning("Oops, didn't add all the vars I wanted to")
    else:
        logging.info("Added all the variables we expected")

    ecu.bind()

    log_handler = log_memory(cfg.logs['csv_filename'], cfg.logs["filename"], cfg.logs["log_line_cache"],
                             time_delay, cfg.logs['csv_required'], cfg.logs["verbose"])

    while 1:
        # get fresh can data or not!
        if ecu.process_all_pages(results):
            logging.debug(pprint.pformat(results))
            for key in (results.keys()):                                            # set index value
                value = int((results.get(key))['value'])                            # pull value from nested dictionary
                short_desc = str((results.get(key))['short_desc']).lstrip()         # pull the short_desc from the dict
                if UDP_tx:
                    mypacket = DataPacket(fmt, short_desc, value)
                    controller.send_packet(mypacket, (cfg.UDP_Dash['host']), (cfg.UDP_Dash['port']) )

            if stdout_dict:
                pp = pprint.PrettyPrinter(indent=cfg.std_out["pp_indent"])
                pp.pprint(results)

            if logger:
                log_handler.new_log(results)

            sleep(0.1)

if __name__ == '__main__':
    main()