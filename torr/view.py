#!/usr/bin/python

import sys
import os
import os.path
import time
import threading

from tkinter import *
from tkinter import ttk

__DELAY__   = 2

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

class UpdateThread(threading.Thread):
    def __init__(self, parent, delay):
        threading.Thread.__init__(self)
        self.parent = parent
        self.go = True
        self.delay = delay
        
    def run(self):
        while self.go:
            self.parent.UpdateList()
            time.sleep(self.delay)
        
        
class ViewGUI:
    def __init__(self, parent, ts, cfg):
        self.version = "gui"
        self.parent = parent
        self.ts  = ts
        self.cfg = cfg
        
        self.InitMenu()
        self.InitUI()
        self.thread = UpdateThread(self, __DELAY__)
        self.thread.start()
    
    def InitMenu(self):
        self.context_menu = Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="Stop",  command=self.StopCurrent)
        self.context_menu.add_command(label="Start", command=self.StartCurrent)
        self.context_menu.add_command(label="Clear", command=self.ClearCurrent)
        self.context_menu.add_command(label="Purge", command=self.PurgeCurrent)
    
    def popup(self, event):
        item = self.tree.item(self.tree.identify("item", event.x, event.y))
        if item["text"] != "":
            self.context_menu.post(event.x_root, event.y_root)
            self.current_item = item["text"]
        else:
            self.context_menu.unpost()
            
    def ClearCurrent(self):
        #logging.info("Clear current torrent [%d]" % self.current_item)
        if sys.platform != "win32":
            self.ts.Remove(self.current_item)
        self.tree.delete(self.current_item)

    def PurgeCurrent(self):
        #logging.info("Purge current torrent [%d]" % self.current_item)
        if sys.platform != "win32":
            self.ts.Purge(self.current_item)
        self.tree.delete(self.current_item)

    def StopCurrent(self):
        #logging.info("Pause current torrent [%d]" % self.current_item)
        if sys.platform != "win32":
            self.ts.Stop(self.current_item)
        #self.Update
    
    def StartCurrent(self):
        #logging.info("Pause current torrent [%d]" % self.current_item)
        if sys.platform != "win32":
            self.ts.Start(self.current_item)
        #self.Update
    
    def InitUI(self):
        self.main_frame   = Frame(self.parent)
        self.top_frame    = Frame(self.parent)
        self.bottom_frame = Frame(self.parent)
        
        self.refreshImage = PhotoImage(file = "./icons/refresh.gif", width=48, height=48)
        self.selectImage  = PhotoImage(file = "./icons/select.gif",  width=48, height=48)
        self.setupImage   = PhotoImage(file = "./icons/setup.gif",   width=48, height=48)
        self.startImage   = PhotoImage(file = "./icons/start.gif",   width=48, height=48)
        self.stopImage    = PhotoImage(file = "./icons/stop.gif",    width=48, height=48)
        self.clearImage   = PhotoImage(file = "./icons/clear.gif",   width=48, height=48)
        self.purgeImage   = PhotoImage(file = "./icons/purge.gif",   width=48, height=48)
        self.exitImage    = PhotoImage(file = "./icons/exit.gif",    width=48, height=48)
        self.addImage     = PhotoImage(file = "./icons/add.gif",     width=48, height=48)
        
        self.add_button     = Button(self.top_frame,    text="Add",        width=48, command=self.AddAll,        image = self.addImage)
        self.refresh_button = Button(self.top_frame,    text="Refresh",    width=48, command=self.UpdateList,    image = self.refreshImage)
        self.clear_button   = Button(self.top_frame,    text="Clear All",  width=48, command=self.Clear,      image = self.clearImage)
        self.purge_button   = Button(self.top_frame,    text="Purge",      width=48, command=self.Purge,         image = self.purgeImage)
        self.select_button  = Button(self.top_frame,    text="Select All", width=48, command=self.SelectAll,     image = self.selectImage)
        self.setup_button   = Button(self.bottom_frame, text="Options",    width=48, command=self.UpdateOptions, image = self.setupImage)
        self.quit_button    = Button(self.bottom_frame, text="Quit",       width=48, command=self.Quit,          image = self.exitImage)
        
        self.tree             = ttk.Treeview(self.main_frame)
        self.v_scroll_tree    = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.tree.yview)
        self.h_scroll_tree    = ttk.Scrollbar(self.main_frame, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscroll=self.v_scroll_tree.set, xscroll=self.h_scroll_tree.set)
        
        self.tree["columns"]=("status", "progress", "name")
        self.tree.column("#0",       width=50,  minwidth=50,  stretch=False)
        self.tree.column("status",   width=110, minwidth=110, stretch=False)
        self.tree.column("progress", width=70,  minwidth=70,  stretch=False)
        self.tree.column("name",     width=350, minwidth=350)
        self.tree.heading("#0",       text="Id")
        self.tree.heading("status",   text="Status")
        self.tree.heading("progress", text="%")
        self.tree.heading("name",     text="Download")
        self.tree.tag_configure("grey",        background="#CCCCCC")
        self.tree.tag_configure("white",       background="#EEEEEE")
        self.tree.tag_configure("downloading", foreground="#104e8b")
        self.tree.tag_configure("seeding",     foreground="#458b00")
        self.tree.tag_configure("stopped",     foreground="#1a1a1a")
        self.tree.tag_configure("checking",    foreground="#8b4500")

        self.tree.bind("<Button-3>", self.popup)
        self.tree.bind("<Button-1>", self.popup)
        
        self.top_frame.grid    (row=0, column=0, sticky=W)
        self.main_frame.grid   (row=1, column=0, sticky=W+E+N+S)
        self.tree.grid         (row=0, column=0, sticky=W+E+N+S)
        self.h_scroll_tree.grid(row=1, column=0, sticky=E+W)
        self.v_scroll_tree.grid(row=0, column=1, sticky=N+S)
        self.bottom_frame.grid (row=2, column=0, sticky=E)

        # gestion de la redimension de la fenetre principale (self.main_frame)
        Grid.rowconfigure   (self.parent,     1, weight=1)
        Grid.columnconfigure(self.parent,     0, weight=1)
        Grid.rowconfigure   (self.main_frame, 0, weight=1, minsize=200)
        Grid.columnconfigure(self.main_frame, 0, weight=1, minsize=580)
        
        self.add_button.grid    (row=0, column=0, padx=2, pady=2)
        self.refresh_button.grid(row=0, column=1, padx=2, pady=2)
        self.clear_button.grid  (row=0, column=2, padx=2, pady=2)
        self.purge_button.grid  (row=0, column=3, padx=2, pady=2)
        self.select_button.grid (row=0, column=4, padx=2, pady=2)
        
        self.setup_button.grid(row=0, column=0, padx=2, pady=2)
        self.quit_button.grid   (row=0, column=1, padx=2, pady=2)

    def UpdateList(self):
        if sys.platform != "win32":
            task_list = self.ts.List()
        else:
            task_list = list()
            task_list.append(Task(id=1, status="downloading", progress="50",  name="My first download"))
            task_list.append(Task(id=2, status="seeding",     progress="100", name="My second download"))
            task_list.append(Task(id=3, status="seeding",     progress="100", name="My third download"))
            task_list.append(Task(id=4, status="stopped",     progress="0",   name="My fourth download"))
            task_list.append(Task(id=5, status="checking",    progress="3",   name="My fifth download"))
        
        if task_list:
            i=0
            background=("grey", "white")
            for task in task_list:
                tag, i = list(), i+1
                tag.append(background[i%2])
                tag.append(task._status)
                if (not self.tree.exists(item=task._id)):
                    # si l'item n'existe pas on le crée avec l'iid = task._id
                    self.tree.insert(parent="",
                                    index="end",
                                    iid=task._id,
                                    text=task._id, 
                                    values=(task._status, "%3.2f" % task._progress, task._name),
                                    tags=(tag))
                else:
                    # on récupère les valeurs de l'item, si le status et la progression sont inchangées on ne fait rien:
                    item = self.tree.item(item=task._id)
                    if ( task._status != item["values"][0] or float(task._progress) != float(item["values"][1]) ):
                        self.tree.item(item=task._id,
                                       text=task._id, 
                                       values=(task._status, "%3.2f" % task._progress, task._name),
                                       tags=(tag))

    def SelectAll(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        
    def Purge(self):
        for item in self.tree.selection():
            if sys.platform != "win32":
                self.ts.Purge(item)
            self.tree.delete(item)

    #def PurgeAll(self):
        #self.SelectAll()
        #self.Purge()

    def Clear(self):
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == "seeding":
                if sys.platform != "win32":
                    self.ts.Remove(item)
                self.tree.delete(item)
            
    def AddAll(self):
        for root, dirs, files in os.walk(self.cfg._input_dir):
            if ( root == self.cfg._input_dir ):
                for f in files:
                    if ( f.rsplit('.', 1)[1] == 'torrent' ): # faire en sorte de prendre en compte cfg.ext + choix multiples
                        self.ts.Add(os.path.join(root,f))
        
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
        
    def Quit(self):
        self.thread.go = False
        self.parent.destroy()