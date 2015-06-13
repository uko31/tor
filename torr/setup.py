#!/usr/bin/python

import argparse
import json
import os
import os.path

class Configuration:
    def __init__(self, filename, 
                 hostname   = "nas", 
                 input_dir  = "%s/dl" % os.getenv("HOME"), 
                 output_dir = "%s/mnt/nas/downloads" % os.getenv("HOME"), 
                 port       = "9091",
                 ext        = "*.torrent"):

        self._filename   = filename
        self._hostname   = hostname
        self._input_dir  = input_dir
        self._output_dir = output_dir
        self._port       = port
        self._ext        = ext

        if os.path.isfile(self._filename):
            try:
                fd = open(self._filename, "r")
                for key, value in dict(json.load(fd)).items():
                    setattr(self, "_%s" % key, value)
                fd.close()
            except IOError as e:
                print("ERROR while tryin to open [%s]" % (e.info, self._filename))
        else:
            self.Update()

    def Update(self):
        if not os.path.isdir(os.path.dirname(self._filename)):
            print(os.path.dirname(self._filename))
            os.makedirs(os.path.dirname(self._filename))
        try:
            fd = open(self._filename, "w")
            string = json.dump({"hostname": "%s" % self._hostname,
                                "input_dir": "%s" % self._input_dir,
                                "output_dir": "%s" % self._output_dir,
                                "port": "%s" % self._port, 
                                "ext": "%s" % self._ext},
                               fd, indent = 4, sort_keys = True)
            fd.close()
        except IOError as e:
            print("ERROR while tryin to open [%s]" % (e.info, self._filename))
        
    def __str__(self):
        s = "Display configuration:\n"
        for key in dir(self):
            if not key.count("__") and not str(getattr(self, key)).count("<bound method") and key.count("_", 0, 1):
                s = "%s >> %-11s : %s\n" % (s, key, getattr(self, key))
        return(s)

class Options:
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog="tor")

        # Grphic User Interface:
        self._parser.add_argument("-g", "--gui", action="store_true", help="launch the GUI")

        # global operations:
        self._parser.add_argument("-d", "--download", action="store_true", help="download all file from the input directory")
        self._parser.add_argument("-l", "--list",     action="store_true", help="display all download tasks")
        self._parser.add_argument("-c", "--clear",    action="store_true", help="remove all finished tasks")
        self._parser.add_argument("-P", "--Purge",    action="store_true", help="purge all download tasks")
        self._parser.add_argument("-v", "--version",  action="store_true", help="version")

        # single operations:
        self._parser.add_argument("-a", "--add",    metavar = "FILENAME", help="download file specified")
        self._parser.add_argument("-r", "--remove", metavar = "ID",       help="remove download task specified by id")
        self._parser.add_argument("-p", "--purge",  metavar = "ID",       help="purge download task specified by id")

        # update configuration:
        self._parser.add_argument("--input",  metavar = "INPUT_DIRECTORY",  help="update input configuration variable")
        self._parser.add_argument("--output", metavar = "OUTPUT_DIRECTORY", help="update output configuration variable")
        self._parser.add_argument("--port",   help="update port configuration variable", type=int)
        self._parser.add_argument("--ext",    help="update ext configuration variable")
        
        self.ParseArgs()

    def ParseArgs(self):
        args = self._parser.parse_args()
        for a in dir(args):
            if not a.count("__") and not a.count("_get"):
                setattr(self, a, getattr(args, a))
        
    def __str__(self):
        s = "Display Options:\n"
    
        if ( self.add ):
            s = "%s >> add: %s\n" % (s, self.add)
        if ( self.download ):
            s = "%s >> download: %s\n" % (s, self.download)
        
        return(s)
