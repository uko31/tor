#!/usr/bin/python

# Author : m.gregoriades@gmail.com
# Date   : Feb. 2015
# Version: 0.2

# classes description:
# - - - - - - - - - - 

# class Task:
#	self._id
#	self._status
#	self._progress
#	self._name
#	self.__init__(self, id, status, progress, name)
#	self.__str__(self)

# class TransmissionServer:
#   self._hostname
#   self._port
#   self._server
#   self.__init__(self, hostname, port)
#   self.Add(self, filename)
#   self.Remove(self, task)
#   self.List(self)
#   self.Purge(Self)
#   self.Clear(Self)
#   (deprecated) self.AddAll(self) - should not be in that class

# class Task:
#	self._id
#	self._status
#	self._progress
#	self._name
#	self.__init__(self, id, status, progress, name)
#	self.__str__(self)

# class DisplayCLI:
#   self.__init__(self)
#	self.ViewList(self, task_list)
#	self.ViewAdd(self, task)
#	self.ViewRemove(self, task)

# class DisplayGUI:
#   self.__init__(self)
#	self.ViewList(self, task_list)
#	self.ViewAdd(self, task)
#	self.ViewRemove(self, task)

# class Configuration:

# class Options:

# required modules:
# - - - - - - - - -
import argparse
import json
import os, os.path
import transmissionrpc
import datetime

# constants:
# - - - - - 
__CONFIG_FILE__ = os.getenv("HOME")+"/.config/tor/config.json"

# code:
# - - -
class Task:
	def __init__(self, id, status, progress, name):
		self._id       = id
		self._status   = status
		self._progress = progress
		self._name     = name

	def __str__(self):
		print("%-3s (%-10s) [%3.Of%%] %s" % (self._id,
											 self._status,
											 self._progress,
											 self._name))
		
class TransmissionServer:
    def __init__(self, hostname, port):
        self._hostname = hostname
        self._port     = port
        try:
            self._conn = transmissionrpc.Client(self._hostname, port=self._port)
        except transmissionrpc.TransmissionError as e:
            print("ERROR: Transmission connection failure [%s] => exiting..." % e.info)
            exit()

    def Add(self, filename):
        try:
            tor = self.tc.add_torrent("file://%s" % os.path.realpath(filename))
			task = Task(tor.id, tor.status, tor.progress, tor.name)
        except transmissionrpc.TransmissionError as e:
            print("ERROR: Download %s not added (reason: %s)" % (os.path.basename(filename), e.info))
            return(False)
            
        print(">> Add download: %s" % (task._name))
        os.remove(torrent)
        return(task)

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
                print("Remove download: %d - %s (completed in: %s)" % (torrent.id, torrent.name, (torrent.date_done-torrent.date_added)))
                self.tc.remove_torrent(torrent.id)
        return(True)
    
    def purge(self):
        # add loop through all available tasks and remove them
        for torrent in self.tc.get_torrents():
            print("Remove download: %d - %s" % (torrent.id, torrent.name))
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
            f = open(self._filename, "r")
            for p, v in dict(json.load(f)).items():
                setattr(self, p, v)
            f.close()
        else:
            #for p, v in dict(json.loads(default_cfg)).item():
                #setattr(self, p, v)
            self.update()

    def update(self):
        if not os.path.isdir(os.path.dirname(self._filename)):
            os.makedirs(os.path.dirname(self._filename))
        f = open(self._filename, "w")
        string = json.dump({"hostname": "%s" % self._hostname,
                            "input_dir": "%s" % self._input_dir,
                            "output_dir": "%s" % self._output_dir,
                            "port": "%s" % self._port, 
                            "ext": "%s" % self._ext},
                           f, indent = 4, sort_keys = True)
        f.close()
        
    def display(self):
        for p in dir(self):
            if not p.count("__") and not str(getattr(self, p)).count("<bound method"):
                print(" >> %-10s : %s" % (p, getattr(self, p)))

class Options:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="tor")

        # global operations:
        self.parser.add_argument("-d", "--download", action="store_true", help="download all file from the input directory")
        self.parser.add_argument("-l", "--list",     action="store_true", help="display all download tasks")
        self.parser.add_argument("-c", "--clear",    action="store_true", help="remove all finished tasks")
        self.parser.add_argument("-p", "--purge",    action="store_true", help="purge all downloadtasks")
        self.parser.add_argument("-v", "--version",  action="store_true", help="version")

        # single operations:
        self.parser.add_argument("-a", "--add",    metavar = "FILENAME", help="download file specified")
        self.parser.add_argument("-r", "--remove", metavar = "ID",       help="remove download task specified by id")

        # update configuration:
        self.parser.add_argument("--input",  metavar = "INPUT_DIRECTORY",  help="update input configuration variable")
        self.parser.add_argument("--output", metavar = "OUTPUT_DIRECTORY", help="update output configuration variable")
        self.parser.add_argument("--port",   help="update port configuration variable", type=int)
        self.parser.add_argument("--ext",    help="update ext configuration variable")

        self.options = self.parser.parse_args()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Main Program
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    
    arg = argument()
    cfg = configuration(__CONFIG_FILE__)
    
    if ( arg.options.input ):
        print("update input configuration variable: %s" % arg.options.input)
        cfg.input_dir = arg.options.input
        cfg.update()

    elif ( arg.options.output ):
        print("update output configuration variable: %s" % arg.options.output)
        cfg.output_dir = arg.options.output
        cfg.update()

    elif ( arg.options.port ):
        print("update port configuration variable: %s" % arg.options.port)
        cfg.port = arg.options.port
        cfg.update()

    elif ( arg.options.ext ):
        print("update port configuration variable: %s" % arg.options.ext)
        cfg.ext = arg.options.ext
        cfg.update()

    else:
        tr = tor(cfg.hostname, cfg.port )
    
        if ( arg.options.add ):
            tr.add(options.add)

        if ( arg.options.remove ):
            tr.remove(options.remove)

        if ( arg.options.download ):
            tr.addall(os.path.realpath(cfg.input_dir))

        if ( arg.options.clear ):
            tr.clear()

        if ( arg.options.purge ):
            tr.purge()
            
        if ( arg.options.list ):
            tr.list()

        if ( arg.options.version ):
            tr.version()
            cfg.display()
