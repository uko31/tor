#!/usr/bin/python

import sys
import os

from tkinter import *

from torr.task  import TransmissionServer
from torr.setup import torr_setup
from torr.setup import torr_option
from torr.view  import ViewCLI
from torr.view  import ViewGUI

if   sys.platform == "linux":
    __CONFIG_FILE__ = os.getenv("HOME")+"/.config/tor/config.json"
elif sys.platform == "win32":
    __CONFIG_FILE__ = ".\\config.json"
    
#==============================================================================
#
#   Main Program
#
#==============================================================================

if __name__ == "__main__":
    
    torr_option.init()
    torr_setup.read()
    
    # graphic mode
    if torr_option.gui:
        if sys.platform != "win32":
            ts = TransmissionServer( torr_setup.hostname, torr_setup.port )
        else:
            ts = None 

        TorGUI = Tk()
        TorGUI.title("Torr: mon gestionnaire de téléchargements")
        ViewGUI(TorGUI, ts)
        TorGUI.mainloop()
    
    # cli mode
    else:
        view = ViewCLI()
        if ( torr_option.input ):
            print("update input configuration variable: %s" % torr_option.input)
            torr_setup.input_dir = torr_option.input
            torr_setup.update()
            torr_setup.display()

        elif ( torr_option.output ):
            print("update output configuration variable: %s" % torr_option.output)
            torr_setup.output_dir = torr_option.output
            torr_setup.update()
            torr_setup.display()

        elif ( torr_option.port ):
            print("update port configuration variable: %s" % torr_option.port)
            torr_setup.port = torr_option.port
            torr_setup.update()
            torr_setup.display()

        elif ( torr_option.ext ):
            print("update port configuration variable: %s" % torr_option.ext)
            torr_setup.ext = torr_option.ext
            torr_setup.update()
            torr_setup.display()

        else:
            if sys.platform != "win32":
                ts = TransmissionServer( torr_setup.hostname, torr_setup.port )
        
            if ( torr_option.add ):
                t = ts.Add(torr_option.add)
                if t:
                    view.Add(t)
                    
            if ( torr_option.remove ):
                view.Remove( ts.Remove(torr_option.remove) )

            if ( torr_option.purge ):
                view.Remove( ts.Remove(torr_option.purge) )
                
            if ( torr_option.download ):
                for root, dirs, files in os.walk(torr_setup.input_dir):
                    if ( root == torr_setup.input_dir ):
                        for f in files:
                            if ( f.rsplit('.', 1)[1] == 'torrent' ): # faire en sorte de prendre en compte torr_setup.ext + choix multiples
                                t = ts.Add(os.path.join(root,f))
                                if t: view.Add(t)

            if ( torr_option.clear ):
                for task in ts.List():
                    if task._status == "seeding":
                        view.Remove( ts.Remove(task._id) )

            if ( torr_option.Purge ):
                for task in ts.List():
                    view.Purge( ts.Purge(task._id) )
                
            if ( torr_option.list ):
                view.List( ts.List() )

            if ( torr_option.version ):
                print(ts.Version())
                torr_setup.display()

