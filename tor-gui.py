#!/usr/bin/python

from tkinter import *
from tkinter import ttk
import sys

class DownloadTable:
    def __init__(self, parent):
        self.parent = parent
        
    def InitUI(self):
        self.frame = Frame(self.parent)
        
class TorGui:
    def __init__(self,parent):
        self.parent = parent
    
    def InitUI(self):
        self.main_frame = Frame(self.parent)
        
        self.download_table = DownloadTable(self.parent)
        self.update_button  = Button(self.main_frame, text="Update")
        self.close_button   = Button(self.main_frame, text="Close")
        
        self.update_button.grid(row = 1, column = 0)
        self.close_button.grid(row = 1, column = 1)

if __name__ == "__main__":
    
    print("begin")

    root = Tk()
    root.title("Tor the GUI")
    TorGui(root)
    root.mainloop()

    print("end")