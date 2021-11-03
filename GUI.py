import os
from tempfile import mkstemp
import tkinter as tk
import tkinter.ttk as ttk
import pygubu
from datablocks import *
from salt import gensaltfile
from cryption import fblockdecryption

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
#PROJECT_UI = os.path.join(PROJECT_PATH, "guitest.ui")
PROJECT_UI = resource_path("guitest.ui")

class GuitestApp:
    def __init__(self, root=None):
        self.root = root
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('master', root)
        try:
            with open(resource_path("enhis.txt"), "r") as f:
                self.builder.get_object('in_salt')['path'] = f.readline().rstrip('\n')
                self.builder.get_object('in_database')['path'] = f.readline().rstrip('\n')
                self.builder.get_object('in_encrypted')['path'] = f.readline().rstrip('\n')
                self.builder.get_object('in_directory')['path'] = f.readline().rstrip('\n')
        except:
            #clean slate
            self.builder.get_object('in_salt')['path'] = "salt"
            self.builder.get_object('in_database')['path'] = "datablock.dbb"
            self.builder.get_object('in_encrypted')['path'] = "encrypted.bin"
            self.builder.get_object('in_directory')['path'] = "test"
        self.builder.get_object('in_directory')['state'] = "disabled"
        
        self.optvar = None
        builder.import_variables(self, ['optvar'])

        builder.connect_callbacks(self)
        root.bind('<Return>', self.commit)

        def historyinit():
            with open(resource_path("enhis.txt"), "w") as f:
                f.write(self.builder.get_object('in_salt')['path'] +'\n')
                f.write(self.builder.get_object('in_database')['path'] +'\n')
                f.write(self.builder.get_object('in_encrypted')['path'] +'\n')
                f.write(self.builder.get_object('in_directory')['path'])
            #root.withdraw()
            #root.focus_set()
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", historyinit)
    
    def optpick(self,pick):
        self.builder.get_object('in_directory')['state'] = "normal"
        self.builder.get_object('in_database')['state'] = "normal"
        self.builder.get_object('in_encrypted')['state'] = "normal"
        self.builder.get_object('label1')['text'] = "Directory encryption"
        if pick == "Decrypt Database":
            self.builder.get_object('in_directory')['state'] = "disabled"
        elif pick == "Generate New Salt":
            self.builder.get_object('in_directory')['state'] = "disabled"
            self.builder.get_object('in_encrypted')['state'] = "disabled"
            self.builder.get_object('in_database')['state'] = "disabled"
        elif pick == "Append Database":
            self.builder.get_object('label1')['text'] = "Directory/file append"
        pass

    def commit(self, dummy=None):
        if self.optvar.get() == "Encrypt Folder":
            try:
                self.mesg("Generating new encrypted tree and binary...")
                #if self.builder.get_object('in_pass').get():
                #    raise 
                dirdatablockandbingen(
                    self.builder.get_object('in_directory')['path'],
                    self.builder.get_object('in_database')['path'],
                    self.builder.get_object('in_encrypted')['path'],
                    self.builder.get_object('in_pass').get(),
                    self.builder.get_object('in_salt')['path']
                )
                self.mesg("Done!")
            except Exception as e:
                self.mesg(e)
        elif self.optvar.get() == "Decrypt Database":
            try:
                dic = {
                    "encr" : self.builder.get_object('in_encrypted')['path'],
                    "key" : self.builder.get_object('in_pass').get(),
                    "salt" : self.builder.get_object('in_salt')['path'],
                }
                tr = Guitree(retreivedatablock(
                    self.builder.get_object('in_database')['path'],
                    dic["key"],
                    dic["salt"]),
                    dic,
                    self.root)
                tr.run()
            except ValueError:
                self.mesg("Password is incorrect!")
        elif self.optvar.get() == "Generate New Salt":
            gensaltfile(self.builder.get_object('in_salt')['path'])
            self.mesg("New salt generated!")
        elif self.optvar.get() == "Append Database":
            try:
                datablockappend(
                    self.builder.get_object('in_directory')['path'],
                    self.builder.get_object('in_pass').get(),
                    self.builder.get_object('in_database')['path'],
                    self.builder.get_object('in_encrypted')['path'],
                    self.builder.get_object('in_salt')['path']
                )
                self.mesg("Done!")
            except ValueError:
                self.mesg("Password is incorrect!")
            except Exception as e:
                self.mesg(e)
        pass

    def mesg(self, text):
        self.builder.get_object('diag')['text'] = text

    def run(self):
        self.mainwindow.mainloop()

class Guitree:
    ptrholder = []
    def __init__(self, datablock=None, dic=None, root=None):
        self.dic=dic

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('decryptree', root)
        self.builder.get_object('dirtree').bind("<Double-1>", self.onclick)
        builder.connect_callbacks(self)
        self.builder.get_object('scrollbar1').configure(command=self.builder.get_object('dirtree').yview)
        self.builder.get_object('dirtree').configure(yscrollcommand=self.builder.get_object('scrollbar1').set)
        def loopDir(parid=0,treeptr=datablock):
            it=0
            for d in treeptr.dirs:
                self.tree.insert('', tk.END, text=d.name, iid=len(self.ptrholder), open=False, tags = ('dir'))
                self.tree.move(len(self.ptrholder),parid,it)
                self.ptrholder.append(d)
                loopDir(len(self.ptrholder)-1, d)
                it+=1
            for d in treeptr.files:
                self.tree.insert('', tk.END, text=d.name, iid=len(self.ptrholder), open=False, tags = ('file'))
                self.tree.move(len(self.ptrholder),parid,it)
                self.ptrholder.append(d)
                it+=1
            
        if isinstance(datablock, Dir):
            self.tree = builder.get_object('dirtree', root)
            for d in datablock.dirs:
                self.tree.insert('', tk.END, text=d.name, iid=len(self.ptrholder), open=False)
                self.ptrholder.append(d)
                loopDir(len(self.ptrholder)-1, d)
        self.tree.tag_configure('dir', background='orange')

    def run(self):
        self.mainwindow.mainloop()
    
    def onclick(self, e):
        item = self.builder.get_object('dirtree').selection()[0]
        #don't overwrite if same named file exists
        if isinstance(self.ptrholder[int(item)], File):
            data = fblockdecryption(
                self.ptrholder[int(item)].head,
                self.ptrholder[int(item)].size,
                self.dic["encr"],
                self.dic["key"],
                self.dic["salt"])
            with open(self.ptrholder[int(item)].name,"wb") as f:
                f.write(data)

if __name__ == '__main__':
    root = tk.Tk()
    app = GuitestApp(root)
    app.run()