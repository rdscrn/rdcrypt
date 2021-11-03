import os
import json
import tkinter as tk
import tkinter.ttk as ttk
from datablocks import *
from salt import gensaltfile
from cryption import fblockdecryption
from ttkwidgets import CheckboxTreeview

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class MainMenu:
    def __init__(self, root=None):
        self.root = root
        root.iconbitmap(resource_path("redcrypt_bTc_icon.ico"))
        root.title('Redcrypt')

        self.optlist = ["Decrypt Database", "Generate New Salt", "Generate New Database", "Append Database"]
        self.option = tk.StringVar(root,"Decrypt Database")
        self.option.trace("w",self.optpick)
        self.optionframe = tk.OptionMenu(root,self.option,*self.optlist)
        self.optionframe.pack()
        #dummy frame to hold width
        tk.Frame(root).pack(ipadx=150)
        
        ttk.Separator(root, orient='horizontal').pack(fill='x',pady=4)

        #get history from file
        try:
            self.data = json.load( open( "history.json" ) )
        except:
            self.data = {"dbb":None, "bin":None, "salt":None}

        self.taskFrame = tk.Frame(root)
        self.taskFrame.pack(fill="x", side="top")
        self.optpick()
        
        #when program is closed save last used directories to file
        def historyinit():
            self.data["dbb"] = self.databEnt.get()
            self.data["bin"] = self.binEnt.get()
            self.data["salt"] = self.saltEnt.get()
            json.dump(self.data, open( "history.json", 'w' ) )
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", historyinit)

    def run(self):
        self.root.mainloop()
    
    def optpick(self,*args):
        #destroy previous task frame elements
        for widget in self.taskFrame.winfo_children():
            widget.destroy()
        #generate new task frame
        if self.option.get() == self.optlist[0]:
            ##decryption frame
            self.databEnt = PickerFrame(self.taskFrame, btext="Database structure", filetypes=[("Database files", "*.dbb"),("all files", "*.*")], ptext=self.data["dbb"])
            self.binEnt = PickerFrame(self.taskFrame, btext="Database binary", filetypes=[("Binary files", "*.bin"),("all files", "*.*")], ptext=self.data["bin"])
            self.saltEnt = PickerFrame(self.taskFrame, btext="Salt", filetypes=[("Salt files", "*.salt"),("all files", "*.*")], ptext=self.data["salt"])

            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            self.passEnt =tk.Entry(self.taskFrame,show="•")
            self.passEnt.pack()
            tk.Label(self.taskFrame,text="Password").pack()
            
            tk.Button(self.taskFrame, text="Decrypt Binary", command= self.commitD, background="green").pack(fill='x')
        elif self.option.get() == self.optlist[1]:
            ##salt generation frame
            self.saltEntNew = tk.Entry(self.taskFrame)
            self.saltEntNew.insert(tk.END, 'salt.salt')
            self.saltEntNew.pack()
            tk.Label(self.taskFrame,text="Salt file").pack()
            
            tk.Button(self.taskFrame, text="Generate new salt file", command= self.commitS, background="green").pack(fill='x')
        elif self.option.get() == self.optlist[2]:
            ##new database generation frame
            self.databEntNew = tk.Entry(self.taskFrame)
            self.databEntNew.insert(tk.END, "database.dbb")
            self.databEntNew.pack()
            tk.Label(self.taskFrame,text="Database structure").pack()
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            self.binEntNew = tk.Entry(self.taskFrame)
            self.binEntNew.insert(tk.END, "encrypted.bin")
            self.binEntNew.pack()
            tk.Label(self.taskFrame,text="Database binary").pack()
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            self.saltEnt = PickerFrame(self.taskFrame, btext="Salt", filetypes=[("Salt files", "*.salt"),("all files", "*.*")], ptext=self.data["salt"])
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            self.passEnt = tk.Entry(self.taskFrame,show="•")
            self.passEnt.pack()
            tk.Label(self.taskFrame,text="Password").pack()
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            tk.Label(self.taskFrame,text="Add files or directories:").pack()
            self.adF = AdderFrame(self.taskFrame)
            
            tk.Button(self.taskFrame, text="Generate new database", command= self.commitN, background="green").pack(fill='x', pady=10)
        elif self.option.get() == self.optlist[3]:
            ##database append frame
            self.databEnt = PickerFrame(self.taskFrame, btext="Pick database file", filetypes=[("Database files", "*.dbb"),("all files", "*.*")], ptext=self.data["dbb"])
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            self.binEnt = PickerFrame(self.taskFrame, btext="Pick binary file", filetypes=[("Binary files", "*.bin"),("all files", "*.*")], ptext=self.data["bin"])
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            self.saltEnt = PickerFrame(self.taskFrame, btext="Pick salt file", filetypes=[("Salt files", "*.salt"),("all files", "*.*")], ptext=self.data["salt"])
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            self.passEnt = tk.Entry(self.taskFrame,show="•")
            self.passEnt.pack()
            tk.Label(self.taskFrame,text="Password").pack()
            
            ttk.Separator(self.taskFrame, orient='horizontal').pack(fill='x',pady=4)
            
            tk.Label(self.taskFrame,text="Add files or directories:").pack()
            self.adF = AdderFrame(self.taskFrame)
            
            tk.Button(self.taskFrame, text="Generate new database", command= self.commitA, background="green").pack(fill='x', pady=10)
        else:
            msg("You shouldn't be here")
        
        self.diag = tk.StringVar(root,"Diagnostics...")
        tk.Label(self.taskFrame, textvariable=self.diag, relief="raised", background="white").pack(fill='x')
        self.root.geometry("")
    
    def msg(self, message):
        self.diag.set(message)
    
    def commitD(self):
        try:
            TreeWindow(self.root, dbb=self.databEnt.get(), bin=self.binEnt.get(), salt=self.saltEnt.get(), key=self.passEnt.get())
        except Exception as e:
            self.msg(e)
    
    def commitS(self):
        txt = self.saltEntNew.get()
        if txt == '':
            txt = "salt.salt"
        saltnew = gensaltfile(txt)
        self.msg("Salt file \""+os.path.basename(saltnew)+"\" has been generated!")
        self.data["salt"] = saltnew
    
    def commitN(self):
        addL = self.adF.getlist()
        if len(addL)<1:
            self.msg("None of given folders or directories are valid.")
            return
        try:
            addL[0]
            dirdatablockandbingen(folderordir=addL[0], datablockn=self.databEntNew.get(), binaryn=self.binEntNew.get(), key=self.passEnt.get(),salt=self.saltEnt.get(),append=False)
            addL.pop(0)
            for item in addL:
                dirdatablockandbingen(folderordir=item, datablockn=self.databEntNew.get(), binaryn=self.binEntNew.get(), key=self.passEnt.get(),salt=self.saltEnt.get(),append=True)
            #update history after successful generation
            self.data["dbb"] = self.databEntNew.get()
            self.data["bin"] = self.binEntNew.get()
            self.data["salt"] = self.saltEnt.get()
        except Exception as e:
            self.msg(e)
        self.msg("New encrypted binary and database generated!")

    def commitA(self):
        addL = self.adF.getlist()
        if len(addL)<1:
            self.msg("None of given folders or directories are valid.")
            return
        try:
            for item in addL:
                dirdatablockandbingen(folderordir=item, datablockn=self.databEnt.get(), binaryn=self.binEnt.get(), key=self.passEnt.get(),salt=self.saltEnt.get(),append=True)
            #update history after successful append
            self.data["dbb"] = self.databEnt.get()
            self.data["bin"] = self.binEnt.get()
            self.data["salt"] = self.saltEnt.get()
        except Exception as e:
            self.msg(e)
        self.msg("Encrypted binary and database appended!")

class TreeWindow:
    def __init__(self, root=None, **kwargs):
        try:
            self.db = retreivedatablock(infolder=kwargs["dbb"],key=kwargs["key"],salt=kwargs["salt"])
        except:
            raise Exception("Unmatching datablock, salt or password")

        self.binary = kwargs["bin"]
        self.key = kwargs["key"]
        self.salt = kwargs["salt"]

        self.root = root
        self.treewindow = tk.Toplevel(root)
        self.treeframe = tk.Frame(self.treewindow)
        self.extractbutton = tk.Button(self.treewindow, text="Extract Selected", command=self.extract)
        self.ptrholder = []
        self.tree = CheckboxTreeview(self.treeframe)
        self.treepopulate(self.db)
        self.scrollbar = tk.Scrollbar(self.treeframe, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.tag_configure('dir', background='#a8baff')
        
        self.treeframe.pack(expand=1, fill=tk.BOTH)
        self.tree.pack(side="left", expand=1, fill=tk.BOTH)
        self.scrollbar.pack(side="right", fill=tk.Y)
        self.extractdirectory = PickerFrame(self.treewindow, btext="Extraction directory" ,dir=True)
        self.extractbutton.pack()
    
    def treepopulate(self, dbptr, parid=''):
        for item in dbptr.dirs:
            self.tree.insert(parid, tk.END, text=item.name, iid=len(self.ptrholder), open=False, tags=("dir",))
            self.ptrholder.append(item)
            self.treepopulate(item,len(self.ptrholder)-1)
        for item in dbptr.files:
            self.tree.insert(parid, tk.END, text=item.name, iid=len(self.ptrholder), open=False, tags=("file",))
            self.ptrholder.append(item)
    
    def extract(self):
        def get_checked():
            checked = []
            def rec_get_checked(item):
                if self.tree.tag_has("checked", item) and self.tree.tag_has("file", item):
                    checked.append(int(item))
                for ch in self.tree.get_children(item):
                    rec_get_checked(ch)
            rec_get_checked('')
            return checked

        def decryptFile(dbptr):
            if not isinstance(dbptr, File):
                raise Exception("Wrong usage of extractFile.")
            return fblockdecryption(head=dbptr.head, block=dbptr.size, input_file = self.binary, key = self.key, salt=self.salt)

        for i in get_checked():
            ip = i
            route=self.tree.item(ip)['text']
            while self.tree.parent(ip) != '':
                ip = self.tree.parent(ip)
                route = self.tree.item(ip)['text']+ '/' + route
            edir = self.extractdirectory.get()
            if edir != '':
                route = self.extractdirectory.get() + '/' + route
            else:
                route = os.getcwd() + '/' + route

            if os.path.exists(route):
                print("Overwrite protection.")
                continue

            try:
                os.makedirs(os.path.dirname(route))
            except:
                pass

            with open(route,"wb") as ou:
                ou.write(decryptFile(self.ptrholder[i]))

class PickerFrame:
    def __init__(self, root, btext="Open", filetypes=[("all files", "*.*")], termin=False, dir=False, ptext=None):
        self.holder = tk.Frame(root)
        self.dir = dir
        self.pathtext = tk.StringVar()
        if ptext is not None:
            self.pathtext.set(ptext)
        self.pathtextbox = tk.Entry(self.holder,textvariable=self.pathtext)
        self.pathbutton = tk.Button(self.holder, text=btext, command= self.callback)
        self.filetypes = filetypes
        if termin:
            self.destroyerbutton = tk.Button(self.holder, text="-", command = self.destroy)

        self.holder.pack(fill="x", side="top")
        if termin:
            self.destroyerbutton.pack(side="left")
        self.pathtextbox.pack(side="left", expand="true", fill="x")
        self.pathbutton.pack(side="right")

    def callback(self):
        if self.dir:
            self.pathtext.set(tk.filedialog.askdirectory())
        else:
            self.pathtext.set(tk.filedialog.askopenfilename(filetypes = self.filetypes))
    
    def destroy(self):
        self.holder.destroy()
    
    def get(self):
        return self.pathtext.get()
    
    def set(self, entry):
        self.pathtext.set(entry)

class AdderFrame:
    pfholder = []
    def __init__(self, root):
        self.buttons = self.buttons = tk.Frame(root)
        self.holder = self.holder = tk.Frame(root)
        self.dirbutton = tk.Button(self.buttons, text="Add directory", command= self.calldir)
        self.filebutton = tk.Button(self.buttons, text="Add file", command= self.callfile)
        
        self.buttons.pack(expand="true", fill="x", pady=4)
        self.filebutton.pack(side="left")
        self.dirbutton.pack(side="right")
        self.holder.pack(expand="true", fill="x")
    
    def callfile(self):
        self.pfholder.append(PickerFrame(self.holder, btext="Select File", termin=True))
    
    def calldir(self):
        self.pfholder.append(PickerFrame(self.holder, btext="Select Directory", termin=True, dir=True))
    
    def getlist(self):
        ret = []
        for item in self.pfholder:
            if os.path.exists(item.get()):
                ret.append(item.get())
        return ret

if __name__ == '__main__':
    root = tk.Tk()
    app = MainMenu(root)
    app.run()