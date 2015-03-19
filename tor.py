#!/usr/bin/python

# Author : m.gregoriades@gmail.com
# Date   : Feb. 2015
# Version: 0.2

# classes description:
# - - - - - - - - - - 

# class Task:
#   _id
#   _status
#   _progress
#   _name
#   __init__(self, id, status, progress, name)
#   __str__(self)

# class TransmissionServer:
#   _hostname
#   _port
#   _server
#   __init__(self, hostname, port)
#   Add(self, filename)
#   Remove(self, task)
#   List(self)
#   Purge(Self)
#   Clear(Self)

# class ViewCLI:
#   __init__(self)
#   List(self, task_list)
#   Add(self, task)
#   Remove(self, task)
#   Purge(self, task)

# class ViewGUI:
#   __init__(self)
#   List(self, task_list)
#   Add(self, task)
#   Remove(self, task)
#   Purge(self, task)

# class Configuration:
#    __init__(self, filename, hostname, port, input_dir, output_dir, ext)
#    Update(self)
#    __str__(self)

# class Options:
#    __init__(self)
#    ParseArgs(self)
#    __str__(self)

# required modules:
# - - - - - - - - -
import argparse
import json
import os
import os.path
import transmissionrpc
import datetime
from tkinter import *
from tkinter import ttk

# constants:
# - - - - - 
__VERSION__ = "0.2.0"
__CONFIG_FILE__ = os.getenv("HOME")+"/.config/tor/config.json"
#__CONFIG_FILE__ = ".\\config.json"

# code:
# - - -
class Task:
    def __init__(self, id, status, progress, name):
        self._id       = id
        self._status   = status
        self._progress = progress
        self._name     = name

    def __str__(self):
        return("%-3s - %-11s - [%3.00f%%] %s" % (self._id, self._status, self._progress, self._name))

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
            tor  = self._conn.add_torrent("file://%s" % os.path.realpath(filename))
            #print(tor.status)
            task = Task(id = tor.id, status = None, progress = 0, name = tor.name)
        except transmissionrpc.TransmissionError as e:
            print("ERROR: Download %s not added (reason: %s)" % (os.path.basename(filename), e.info))
            return(False)
            
        os.remove(filename)
        return(task)

    def Remove(self, id):
        tor = self._conn.get_torrent(id)
        task = Task(tor.id, tor.status, tor.progress, tor.name)
        self._conn.remove_torrent(id)
        return(task)

    def Purge(self, id):
        tor = self._conn.get_torrent(id)
        task = Task(tor.id, tor.status, tor.progress, tor.name)
        self._conn.remove_torrent(id, delete_data=True)
        return(task)
    
    def List(self):
        tasks = list()

        torrents = self._conn.get_torrents()
        if len(torrents) != 0:
            for torrent in torrents:
                tasks.append(Task(torrent.id, torrent.status, torrent.progress, torrent.name))
            return(tasks)
        else:
            return(False)

    def Version(self):
        return("version: %s", __VERSION__)
        
    # def __str__(self):

class ViewCLI:
    def __init__(self):
        self.display = "cli"
        
    def List(self, task_list):
        for t in task_list:
            print(t)
    
    def Add(self, task):
        print(">> Add download: %s" % (task._name))
        return(True)
        
    def Remove(self, task):
        print(">> Remove download: %d - %s" % (task._id, task._name))
        return(True)

    def Purge(self, task):
        print(">> Purge download: %d - %s" % (task._id, task._name))
        return(True)

class ViewGUI:
    def __init__(self, parent):
        self.display = "gui"
        self.parent = parent
        
    def List(self, task_list):
        return(True)
        
    def Add(self, task):
        return(True)
        
    def Remove(self, task):
        return(True)

    def Purge(self, task):
        return(True)

        
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
                    setattr(self, key, value)
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
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Main Program
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    
    opt = Options()
    cfg = Configuration(__CONFIG_FILE__)
    
    # graphic mode
    if opt.gui:
        TorGUI = Tk()
        TorGUI.title("Tor - the GUI")
        ViewGUI(TorGUI)
        TorGUI.mainloop()
    
    # cli mode
    else:
        view = ViewCLI()
        if ( opt.input ):
            print("update input configuration variable: %s" % opt.input)
            cfg.input_dir = opt.input
            cfg.Update()
            print(cfg)

        elif ( opt.output ):
            print("update output configuration variable: %s" % opt.output)
            cfg.output_dir = opt.output
            cfg.Update()
            print(cfg)

        elif ( opt.port ):
            print("update port configuration variable: %s" % opt.port)
            cfg.port = opt.port
            cfg.Update()
            print(cfg)

        elif ( opt.ext ):
            print("update port configuration variable: %s" % opt.ext)
            cfg.ext = opt.ext
            cfg.Update()
            print(cfg)

        else:
            ts = TransmissionServer( cfg.hostname, cfg.port )
        
            if ( opt.add ):
                view.Add( ts.Add(opt.add) )

            if ( opt.remove ):
                view.Remove( ts.Remove(opt.remove) )

            if ( opt.purge ):
                view.Remove( ts.Remove(opt.purge) )
                
            if ( opt.download ):
                for root, dirs, files in os.walk(cfg.input_dir):
                    if ( root == cfg.input_dir ):
                        for f in files:
                            if ( f.rsplit('.', 1)[1] == 'torrent' ):
                                view.Add( ts.Add(os.path.join(root,f)) )

            if ( opt.clear ):
                for task in ts.List():
                    if task._status == "seeding":
                        view.Remove( ts.Remove(task._id) )

            if ( opt.Purge ):
                for task in ts.List():
                    view.Purge( ts.Purge(task._id) )
                
            if ( opt.list ):
                view.List( ts.List() )

            if ( opt.version ):
                ts.version()
                cfg.display()
