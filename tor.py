#!/usr/bin/python

# Author  : Uko31 at github dot com
# Date    : Feb. 2015
# Version : 0.2

# classes description:
# - - - - - - - - - - 

# class Task:
#   _id
#   _status
#   _progress
#   _name
#   __init__(self, id, name, status = None, progress =0)
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
#   Version(self)

# class ViewCLI:
#   __init__(self)
#   List(self, task_list)
#   Add(self, task)
#   Remove(self, task)
#   Purge(self, task)

# class ViewGUI:
#   __init__(self, ts, cfg)
#   UpdateList(self, task_list)
#   Remove(self)
#   Purge(self)
#   Clear(self)
#   PurgeAll(self)
#   UpdateOptions(self)
#   ProcessOptions(self)

# class Configuration:
#   _hostname
#   _port
#   _input_dir
#   _output_dir
#   _ext
#   __init__(self, filename, hostname, port, input_dir, output_dir, ext)
#   Update(self)
#   __str__(self)

# class Options:
#   __init__(self)
#   ParseArgs(self)
#   __str__(self)

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
# __CONFIG_FILE__ = ".\\config.json"

# code:
# - - -
class Task:
    def __init__(self, id, name, status = None, progress = 0):
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
            task = Task(id = tor.id, name = tor.name)
        except transmissionrpc.TransmissionError as e:
            print("ERROR: Download %s not added (reason: %s)" % (os.path.basename(filename), e.message))
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
                tasks.append(Task(id=torrent.id, 
                                  status=torrent.status, 
                                  progress=torrent.progress, 
                                  name=torrent.name))
            return(tasks)
        else:
            return(False)

    def Version(self):
        return("version: %s", __VERSION__)
        
    # def __str__(self):

class ViewCLI:
    def __init__(self):
        self.version = "cli"
        
    def List(self, task_list):
        if task_list:
            for t in task_list:
                print(t)
        else:
            print("No task queued.")
    
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
    def __init__(self, parent, ts, cfg):
        self.version = "gui"
        self.parent = parent
        self.ts  = ts
        self.cfg = cfg
        
        self.InitUI()
        # self.UpdateList()
    
    def InitUI(self):
        self.top_frame    = Frame(self.parent)
        self.bottom_frame = Frame(self.parent)
        
        #self.refreshImage = PhotoImage(file = "refresh.gif",       width=32, height=32)
        #self.exitImage    = PhotoImage(file = "exit.gif",          width=32, height=32)
        #self.garbageImage = PhotoImage(file = "garbage.gif",       width=45, height=32)
        #self.trashImage   = PhotoImage(file = "trash.gif",         width=32, height=32)
        #self.setupImage   = PhotoImage(file = "setup-options.gif", width=32, height=32)
        #self.clearImage   = PhotoImage(file = "clear-icon.gif",    width=32, height=32)
        #self.selectImage  = PhotoImage(file = "select-all.gif",    width=32, height=32)
        
        self.refresh_button   = Button(self.top_frame,    text="Refresh",      command=self.UpdateList)#,    image = self.refreshImage)
        self.clear_button     = Button(self.top_frame,    text="Clear",        command=self.Clear)#,         image = self.clearImage)
        self.purge_button     = Button(self.top_frame,    text="Purge",        command=self.Purge)#,         image = self.trashImage)
        self.purgeall_button  = Button(self.top_frame,    text="Purge All",    command=self.PurgeAll)#,      image = self.garbageImage)
        self.selectall_button = Button(self.top_frame,    text = "Select All", command=self.SelectAll)#,     image = self.selectImage)
        self.options_button   = Button(self.bottom_frame, text="Options",      command=self.UpdateOptions)#, image = self.setupImage)
        self.quit_button      = Button(self.bottom_frame, text="Quit",         command=quit)#,               image = self.exitImage)
        self.tree             = ttk.Treeview(self.parent)
        
        self.tree["columns"]=("status", "progress", "name")
        self.tree.column("#0",       width=50)
        self.tree.column("status",   width=110)
        self.tree.column("progress", width=70)
        self.tree.column("name",     width=350)
        self.tree.heading("#0",       text="Id")
        self.tree.heading("status",   text="Status")
        self.tree.heading("progress", text="%")
        self.tree.heading("name",     text="Download")

        self.top_frame.grid   (row=0, column=0)
        self.tree.grid        (row=1, column=0)
        self.bottom_frame.grid(row=2, column=0)
        
        self.refresh_button.grid  (row=0, column=0)
        self.clear_button.grid    (row=0, column=1)
        self.purge_button.grid    (row=0, column=2)
        self.purgeall_button.grid (row=0, column=3)
        self.selectall_button.grid(row=0, column=4)
        
        self.options_button.grid(row=0, column=0)
        self.quit_button.grid   (row=0, column=1)

    def UpdateList(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        task_list = self.ts.List()
        if task_list:
            for task in task_list:
                self.tree.insert("", 
                                 "end", 
                                 text=task._id, 
                                 values=(task._status, "%3.2f" % task._progress, task._name))

    def SelectAll(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        
    def Purge(self):
        for item in self.tree.selection():
            self.ts.Purge(self.tree.item(item)["text"])
            self.tree.delete(item)

    def PurgeAll(self):
        self.SelectAll()
        self.Purge()

    def Clear(self):
        for item in self.tree.selection():
            self.ts.Remove(self.tree.item(item)["text"])
            self.tree.delete(item)
        
    def UpdateOptions(self):
        self.updateInput    = StringVar()
        self.updateOutput   = StringVar()
        self.updateHostname = StringVar()
        self.updatePort     = StringVar()
        self.updateExt      = StringVar()

        self.updateInput.set(self.cfg._input_dir)
        self.updateOutput.set(self.cfg._output_dir)
        self.updateHostname.set(self.cfg._hostname)
        self.updatePort.set(self.cfg._port)
        self.updateExt.set(self.cfg._ext)
    
        options = Toplevel()
        inputLabel    = Label (options, text = "Input Directory:")
        outputLabel   = Label (options, text = "Output Directory:")
        hostnameLabel = Label (options, text = "Hostname:")
        portLabel     = Label (options, text = "Port:")
        extLabel      = Label (options, text = "Extensions:")

        inputEntry    = Entry (options, textvariable = self.updateInput) 
        outputEntry   = Entry (options, textvariable = self.updateOutput)
        hostnameEntry = Entry (options, textvariable = self.updateHostname)
        portEntry     = Entry (options, textvariable = self.updatePort)
        extEntry      = Entry (options, textvariable = self.updateExt)
        okButton      = Button(options, text = "Ok", command=self.ProcessOptions)
        
        inputLabel.   grid(row = 0, column = 0)
        outputLabel.  grid(row = 1, column = 0)
        hostnameLabel.grid(row = 2, column = 0)
        portLabel.    grid(row = 3, column = 0)
        extLabel.     grid(row = 4, column = 0)
        
        inputEntry.   grid(row = 0, column = 1)
        outputEntry.  grid(row = 1, column = 1)
        hostnameEntry.grid(row = 2, column = 1)
        portEntry.    grid(row = 3, column = 1)
        extEntry.     grid(row = 4, column = 1)
        
        okButton.     grid(row = 5, column = 1)
       
    def ProcessOptions(self):
        self.cfg._input_dir  = self.updateInput.get()
        self.cfg._output_dir = self.updateOutput.get()
        self.cfg._hostname   = self.updateHostname.get()
        self.cfg._port       = self.updatePort.get()
        self.cfg._ext        = self.updateExt.get()
        self.cfg.Update()
        
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
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Main Program
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    
    opt = Options()
    cfg = Configuration(__CONFIG_FILE__)
    
    # graphic mode
    if opt.gui:
        ts = TransmissionServer( cfg._hostname, cfg._port )
        # ts = "toto"
        TorGUI = Tk()
        TorGUI.title("Tor - the GUI")
        ViewGUI(TorGUI, ts, cfg)
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
            ts = TransmissionServer( cfg._hostname, cfg._port )
        
            if ( opt.add ):
                t = ts.Add(opt.add)
                if t:
                    view.Add(t)
                    
            if ( opt.remove ):
                view.Remove( ts.Remove(opt.remove) )

            if ( opt.purge ):
                view.Remove( ts.Remove(opt.purge) )
                
            if ( opt.download ):
                for root, dirs, files in os.walk(cfg.input_dir):
                    if ( root == cfg.input_dir ):
                        for f in files:
                            if ( f.rsplit('.', 1)[1] == 'torrent' ): # faire en sorte de prendre en compte cfg.ext + choix multiples
                                t = ts.Add(os.path.join(root,f))
                                if t: view.Add(t)

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
