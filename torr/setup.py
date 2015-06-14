#!/usr/bin/python

import argparse
import json
import os
import os.path

class torr_setup:
    filename   = "%s/.config/torr/setup.json" % os.getenv("HOME")
    hostname   = "nas"
    port       = 9091
    ext        = "*.torrent"
    input_dir  = "%s/dl" % os.getenv("HOME")
    output_dir = "%s/mnt/nas/downloads" % os.getenv("HOME")
    
    @staticmethod
    def read():
        if os.path.isfile(torr_setup.filename):
            try:
                fd = open(torr_setup.filename, "r")
                for key, value in dict(json.load(fd)).items():
                    setattr(torr_setup, "%s" % key, value)
                fd.close()
            except IOError as e:
                print("ERROR while tryin to open [%s]" % (e.info, torr_setup.filename))
        else:
            torr_setup.update()

    @staticmethod
    def update():
        if not os.path.isdir(os.path.dirname(torr_setup.filename)):
            print( os.path.dirname(torr_setup.filename) )
            os.makedirs( os.path.dirname(torr_setup.filename) )
        try:
            fd = open(torr_setup.filename, "w")
            string = json.dump( {"hostname": "%s"   % torr_setup.hostname,
                                 "input_dir": "%s"  % torr_setup.input_dir,
                                 "output_dir": "%s" % torr_setup.output_dir,
                                 "port": "%s"       % torr_setup.port, 
                                 "ext": "%s"        % torr_setup.ext},
                                fd, indent = 4, sort_keys = True)
            fd.close()
        except IOError as e:
            print("ERROR while tryin to open [%s]" % (e.info, torr_setup.filename))

    @staticmethod
    def display():
        s = "Display configuration:\n"
        for key in dir(torr_setup):
            if not key.count("__") and not str(getattr(torr_setup, key)).count("<function"):
                s = "%s >> %-11s : %s\n" % (s, key, getattr(torr_setup, key))
        print(s)

class torr_option:
    @staticmethod
    def init():
        torr_option.parser = argparse.ArgumentParser(prog="torr")

        # Graphic User Interface:
        torr_option.parser.add_argument("-g", "--gui", action="store_true", help="launch the GUI")

        # global operations:
        torr_option.parser.add_argument("-d", "--download", action="store_true", help="download all file from the input directory")
        torr_option.parser.add_argument("-l", "--list",     action="store_true", help="display all download tasks")
        torr_option.parser.add_argument("-c", "--clear",    action="store_true", help="remove all finished tasks")
        torr_option.parser.add_argument("-P", "--Purge",    action="store_true", help="purge all download tasks")
        torr_option.parser.add_argument("-v", "--version",  action="store_true", help="version")

        # single operations:
        torr_option.parser.add_argument("-a", "--add",    metavar = "FILENAME", help="download file specified")
        torr_option.parser.add_argument("-r", "--remove", metavar = "ID",       help="remove download task specified by id")
        torr_option.parser.add_argument("-p", "--purge",  metavar = "ID",       help="purge download task specified by id")

        # update configuration:
        torr_option.parser.add_argument("--input",  metavar = "INPUT_DIRECTORY",  help="update input configuration variable")
        torr_option.parser.add_argument("--output", metavar = "OUTPUT_DIRECTORY", help="update output configuration variable")
        torr_option.parser.add_argument("--port",   help="update port configuration variable", type=int)
        torr_option.parser.add_argument("--ext",    help="update ext configuration variable")
        
        # parse arguments & set static attributes:
        args = torr_option.parser.parse_args()
        for arg in dir(args):
            if not arg.count("__") and not arg.count("_get"):
                setattr(torr_option, arg, getattr(args, arg))
    
    @staticmethod
    def display():
        s = "Display Options:\n"
    
        if ( torr_option.add ):
            s = "%s >> add: %s\n" % (s, torr_option.add)
        if ( torr_option.download ):
            s = "%s >> download: %s\n" % (s, torr_option.download)
        
        print(s)

    