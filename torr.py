#!/usr/bin/python

import sys
import os

from tkinter import *

from torr.task  import TransmissionServer
from torr.setup import Options
from torr.setup import Configuration
from torr.view  import ViewCLI
from torr.view  import ViewGUI

if   sys.platform == "linux":
    __CONFIG_FILE__ = os.getenv("HOME")+"/.config/tor/config.json"
elif sys.platform == "win32":
    __CONFIG_FILE__ = ".\\config.json"
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main Program
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    
    opt = Options()
    cfg = Configuration(__CONFIG_FILE__)
    
    # graphic mode
    if opt.gui:
        if sys.platform != "win32":
            ts = TransmissionServer( cfg._hostname, cfg._port )
        else:
            ts = None 

        TorGUI = Tk()
        TorGUI.title("Torr: mon gestionnaire de téléchargements")
        ViewGUI(TorGUI, ts, cfg)
        TorGUI.mainloop()
    
    # cli mode
    else:
        view = ViewCLI()
        if ( opt.input ):
            print("update input configuration variable: %s" % opt.input)
            cfg._input_dir = opt.input
            cfg.Update()
            print(cfg)

        elif ( opt.output ):
            print("update output configuration variable: %s" % opt.output)
            cfg._output_dir = opt.output
            cfg.Update()
            print(cfg)

        elif ( opt.port ):
            print("update port configuration variable: %s" % opt.port)
            cfg._port = opt.port
            cfg.Update()
            print(cfg)

        elif ( opt.ext ):
            print("update port configuration variable: %s" % opt.ext)
            cfg._ext = opt.ext
            cfg.Update()
            print(cfg)

        else:
            if sys.platform != "win32":
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
                for root, dirs, files in os.walk(cfg._input_dir):
                    if ( root == cfg._input_dir ):
                        for f in files:
                            if ( f.rsplit('.', 1)[1] == 'torrent' ): # faire en sorte de prendre en compte cfg._ext + choix multiples
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
                print(cfg)

