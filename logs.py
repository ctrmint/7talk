import os
import csv

class log_memory(object):
    """
    Class for storing logs in RAM then output to disk.
    Logs are initially stored in memory (list) until limit reach at which point log lines (list) are written to disk.
    Memory(list) then cleared, and further lines stored.  Approach used to reduce IO hit on SBC.

    Currently two logging formats supported, verbose or other.  Verbose writes full dictionary structure, other writes
    only values
    992,178.56000000000424,"RT_AIRTEMP1(LIM),16.189669642175936","RT_COOLANTTEMP1(LIM),21.95635919737545",
    "RT_BATTERYVOLTAGE(LIM),0.0","RT_SOFTCUTTIME,7800.0","RT_HARDCUTTIME,7900.0",

    Lines are prefixed with total line count and simulated timing value, value based 0 + ECU poll wait value.

    """
    def __init__(self, csv_filename, filename, lines_to_cache, timing, req_csv, verbose):
        self.csv_filename = csv_filename                    # Filename of cvs output file
        self.filename = filename                            # Filename of log output file.
        self.lines_to_cache = lines_to_cache                # Volume of lines to cache before writing to disk.
        #self.log_line = "New log \n"                        # First line in log file
        self.stored_lines = []                              # All logs cached prior to writing to disk.
        #self.stored_lines.append(self.log_line)             # add first line to cache
        self.timing = timing                                # Timing interval, used to simulate time value.
        self.csv = req_csv
        self.time_inc = 0                                   # Time incremental counter, increments based on timing value.
        self.line_counter = 0                               # Counter, increments per results set, applied to log line.
        self.cache_count = 0
        self.verbose = verbose                              # Level of verbosity of log line.
        self.csv_header_written = False
        self.csv_lines = []

    def write_to_disk(self):                                #
        fo = open(self.filename, 'a+')                       # open object for file
        fo.seek(0, os.SEEK_END)                             # goto end of file
        fo.writelines(self.stored_lines)                    # write lines to file
        fo.close()                                          # close file
        self.stored_lines.clear()
        self.cache_count = 0
        return

    def write_csv(self):
        with open(self.csv_filename, 'a+', newline='') as csvfile:
            # following names should be dynamically set.... future improvement.
            fieldnames = ['time_interval', 'name', 'value', 'short_desc', 'units']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not self.csv_header_written:
                writer.writeheader()
                self.csv_header_written = True

            for line in self.csv_lines:
                writer.writerow(line)

            self.csv_lines.clear()
            self.cache_count = 0
        return

    def new_log(self, newline):
        self.log_line = newline
        line_to_store = ""

        if type(self.log_line) == dict:                    # check to make sure the line is a dict, as expected.
            dictList = self.log_line.values()
            self.line_counter += 1
            self.time_inc += self.timing
            self.cache_count += 1

            for element in dictList:
                if self.csv:                               # added CVS support,
                    dict_to_write = {"time_interval": self.time_inc}
                    dict_to_write.update(element)
                    self.csv_lines.append(dict_to_write)            # may retire other formats and tidy up,
                                                                    # once optimal format decided.

                if self.verbose:
                    line_to_store = line_to_store + ('{0},{1},{2}'.format(self.line_counter, self.time_inc, element))
                else:
                    line_to_store = line_to_store + ('"{0},{1}",'.format(element['name'],element['value']))

            line_to_store = str(self.line_counter) + "," + str(self.time_inc) + "," + str(line_to_store)

        else:
            self.stored_lines.append(self.log_line)                        # write the line to cache even if not dict

        self.stored_lines.append(line_to_store + "\n")                     # write line, whatever format to the buffer

        if self.cache_count > self.lines_to_cache:                        # if cache limit reached, write logs to disk.
            self.write_to_disk()
            self.write_csv()

        if self.line_counter > 400000000:                                  # if log lines reach 400000000, reset.
            self.line_counter = 1                                          # don't want counters being too large in
            self.time_inc = 1                                              # memory.
        return
