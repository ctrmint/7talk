import os
class log_memory(object):
    def __init__(self, filename, lines_to_cache, timing, verbose):
        self.filename = filename                            # Filename of log output file.
        self.lines_to_cache = lines_to_cache                # Volume of lines to cache before writing to disk.
        self.log_line = "New log \n"                        # First line in log file
        self.stored_lines = []                              # All logs cached prior to writing to disk.
        self.stored_lines.append(self.log_line)             # add first line to cache
        self.timing = timing                                # Timing interval, used to simulate time value.
        self.time_inc = 0                                   # Time incremental counter, increments based on timing value.
        self.line_counter = 0                               # Counter, increments per results set, applied to log line.
        self.verbose = verbose                              # Level of verbosity of log line.


    def write_to_disk(self):                                #
        fo = open(self.filename, 'w')                       # open object for file
        fo.seek(0, os.SEEK_END)                             # goto end of file
        fo.writelines(self.stored_lines)                    # write lines to file
        fo.close()                                          # close file


    def new_log(self, newline):
        self.log_line = newline
        line_to_store = ""

        if type(self.log_line) == dict:                    # check to make sure the line is a dict, as expected.
            dictList = self.log_line.values()
            self.line_counter += 1
            self.time_inc += self.timing
            for element in dictList:
                if self.verbose:
                    line_to_store = line_to_store + ('{0},{1},{2}'.format(self.line_counter, self.time_inc, element))
                else:
                    line_to_store = line_to_store + ('"{0},{1}",'.format(element['name'],element['value']))

            line_to_store = str(self.line_counter) + "," + str(self.time_inc) + "," + str(line_to_store)

        else:
            self.stored_lines.append(self.log_line)                        # write the line to cache even if not dict

        self.stored_lines.append(line_to_store + "\n")                     # write line, whatever format to the buffer

        if self.line_counter > self.lines_to_cache:                        # if cache limit reached, write logs to disk.
            self.write_to_disk()

        if self.line_counter > 400000000:                                  # if log lines reach 400000000, reset.
            self.line_counter = 1                                          # don't want counters being too large in
            self.time_inc = 1                                              # memory.

