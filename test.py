#!/usr/bin/python

from tkinter import *
from tkinter import ttk

data = [{"id":523, "status":"Downloading", "progress":"98%",  "file":"This is a file and a big one !"                  }, 
        {"id":524, "status":"Seeding",     "progress":"100%", "file":"Another huge file with an even more complex name"},
        {"id":525, "status":"hold",        "progress":"0%",   "file":"this download is held for later or never"        }]

class tree:
    def __init__(self, parent):
        self.parent = parent
        self.InitUI()
        self.InitData()
    
    def InitUI(self):
        self.frame = Frame(self.parent)
        self.select_all_button = Button(self.frame, text = "Select All", command = self.SelectAll)
        self.delete_button = Button(self.frame, text = "delete", command = self.DeleteSelected)
        self.tree = ttk.Treeview(self.frame)
        self.tree["columns"]=("status", "progress", "name")
        self.tree.column("#0",       width=50)
        self.tree.column("status",   width=110)
        self.tree.column("progress", width=70)
        self.tree.column("name",     width=350)
        self.tree.heading("#0",     text="Id")
        self.tree.heading("status", text="Status")
        self.tree.heading("progress", text="%")
        self.tree.heading("name",   text="Download")
        self.action = Button(self.frame, text="Action", command=self.Action)
        
        self.frame.grid()
        self.select_all_button.grid(row = 0, column = 0)
        self.delete_button.grid    (row = 0, column = 1)
        self.tree.grid             (row = 1, column = 0, columnspan = 2)
        self.action.grid           (row = 2, column = 0, )

    def InitData(self):
        for d in data:
            self.tree.insert("", "end", text=d["id"], values=(d["status"], d["progress"], d["file"]))

    def SelectAll(self):
        item = "I001"
        if self.tree.exists(item):
            while self.tree.next(item) != '':
                self.tree.selection_add(item)
                item = self.tree.next(item)
            self.tree.selection_add(item)
    
    def DeleteSelected(self):
        for item in self.tree.selection():
            print("Delete item: %s (id = item(%s))" % (item, self.tree.item(item)["text"]))
            self.tree.delete(item)
    
    def Action(self):
        for i in self.tree.selection():
            print("select: %s %s" % (i, self.tree.item(i)))

# = = = = = = = = = = = = = = = = = = = =

if __name__ == "__main__":
    
    root = Tk()
    root.title("test")
    tree(root)
    root.mainloop()