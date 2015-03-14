#!/usr/bin/python

import argparse
import json
import os, os.path
import transmissionrpc
import datetime

__CONFIG_FILE__ = os.getenv("HOME")+"/.config/tor/config.json"

class tor:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        try:
            self.tc = transmissionrpc.Client(self.hostname, port=self.port)
        except transmissionrpc.TransmissionError as e:
            print("Transmission connection error [%s] => exiting..." % e.info)
            exit()
          

    def add(self, torrent):
        try:
            tor = self.tc.add_torrent("file://%s" % os.path.realpath(torrent))
        except transmissionrpc.TransmissionError as e:
            print("! Torrent: %s not added:%s" % (os.path.basename(torrent), e.message))
            return(False)
            
        print(">> Ad torrent: %s" % (tor.name))
        os.remove(torrent)
        return(True)

    def addall(self, path):
        for root, dirs, files in os.walk(path):
            if ( root == path ):
                for f in files:
                    if ( f.rsplit('.', 1)[1] == 'torrent' ):
                        self.add(os.path.join(root,f))

    def remove(self, id):
        self.tc.remove_torrent(id)

    def clear(self):
        # add a loop through all available torrent and remove finished ones
        for torrent in self.tc.get_torrents():
            if torrent.status == "seeding":
                print("remove torrent: %d - %s (completed in: %s)" % (torrent.id, torrent.name, (torrent.date_done-torrent.date_added)))
                self.tc.remove_torrent(torrent.id)
        return(True)
    
    def purge(self):
        # add loop through all available tasks and remove them
        for torrent in self.tc.get_torrents():
            print("remove torrent: %d - %s" % (torrent.id, torrent.name))
            self.tc.remove_torrent(torrent.id, delete_data=True)
        return(True)
    
    def list(self):
        # a a loop to dipslay each and every tasks.
        torrents = self.tc.get_torrents()
        if len(torrents) != 0:
            for torrent in torrents:
                print("%d - %-11s - %3.0f%% - %s" % (torrent.id, torrent.status, torrent.progress, torrent.name))
            return(True)
        else:
            print("No download queued")
            return(False)

    def version(self):
        print("version: 0.1")

class configuration:
    def __init__(self, filename, 
                 hostname   = "nas", 
                 input_dir  = os.getenv("HOME")+"/dl", 
                 output_dir = os.getenv("HOME")+"/mnt/nas/downloads", 
                 port       = "9091",
                 ext        = "*.torrent",
                 sqlite     = os.getenv("HOME")+"/mnt/nas/downloads/.database"):
        self.filename = filename
        
        self.hostname   = hostname
        self.input_dir  = input_dir
        self.output_dir = output_dir
        self.port       = port
        self.ext        = ext
        self.sqlite     = sqlite

        if os.path.isfile(self.filename):
            f = open(self.filename, "r")
            for p, v in dict(json.load(f)).items():
                setattr(self, p, v)
            f.close()
        else:
            #for p, v in dict(json.loads(default_cfg)).item():
                #setattr(self, p, v)
            self.update()

    def update(self):
        if not os.path.isdir(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))
        f = open(self.filename, "w")
        string = json.dump({"hostname": "%s" % self.hostname,
                            "input_dir": "%s" % self.input_dir,
                            "output_dir": "%s" % self.output_dir,
                            "port": "%s" % self.port, 
                            "ext": "%s" % self.ext,
                            "sqlite": "%s" % self.sqlite},
                           f, indent = 4, sort_keys = True)
        f.close()
        
    def display(self):
        for p in dir(self):
            if not p.count("__") and not str(getattr(self, p)).count("<bound method"):
                print(" >> %-10s : %s" % (p, getattr(self, p)))

class argument:
    def __init__(self):
        self.parser = argparse.ArgumentParser()

        # global operations:
        self.parser.add_argument("-d", "--download", action="store_true", help="download all file from the input directory")
        self.parser.add_argument("-l", "--list",     action="store_true", help="display all download tasks")
        self.parser.add_argument("-c", "--clear",    action="store_true", help="remove all finished tasks")
        self.parser.add_argument("-p", "--purge",    action="store_true", help="purge all downloadtasks")
        self.parser.add_argument("-v", "--version",  action="store_true", help="version")

        # single operations:
        self.parser.add_argument("-a", "--add",    help="download file specified")
        self.parser.add_argument("-r", "--remove", help="remove download task specified by id")

        # update configuration:
        self.parser.add_argument("--input",  help="update input configuration variable")
        self.parser.add_argument("--output", help="update output configuration variable")
        self.parser.add_argument("--port",   help="update port configuration variable", type=int)
        self.parser.add_argument("--ext",    help="update ext configuration variable")

        self.options = self.parser.parse_args()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Main Program
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    
    arg = argument()
    cfg = configuration(os.path.realpath(__CONFIG_FILE__))
    tr = tor(cfg.hostname, cfg.port )
    
    if ( arg.options.input ):
        print("update input configuration variable: %s" % arg.options.input)
        cfg.input_dir = options.input
        cfg.update()

    if ( arg.options.output ):
        print("update output configuration variable: %s" % arg.options.output)
        cfg.output_dir = options.output
        cfg.update()

    if ( arg.options.port ):
        print("update port configuration variable: %s" % arg.options.port)
        cfg.port = options.port
        cfg.update()

    if ( arg.options.ext ):
        print("update port configuration variable: %s" % arg.options.ext)
        cfg.ext = options.ext
        cfg.update()

    if ( arg.options.add ):
        tr.add(options.add)

    if ( arg.options.remove ):
        tr.remove(options.remove)

    if ( arg.options.download ):
        tr.addall(os.path.realpath(cfg.input))

    if ( arg.options.clear ):
        tr.clear()

    if ( arg.options.purge ):
        tr.purge()
        
    if ( arg.options.list ):
        tr.list()

    if ( arg.options.version ):
        tr.version()
        cfg.display()
