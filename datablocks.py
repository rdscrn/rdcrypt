import os
import sys
from cryption import *
import pickle
import logging

class File:
    def __init__(self, nam = None ,siz = 0, he = 0):
        self.name = nam
        self.head = he
        self.size = siz

class Dir:
    def __init__(self, nam, f = [] , d = []):
        self.name = nam
        self.files = f
        self.dirs = d
    def prdir(self, depth=0):
        print(" " * depth +self.name)
        for dir in self.dirs:
            dir.prdir(depth+1)
        for fil in self.files:
            print(" " * (depth+1) + fil.name + ' ' + str(fil.head) + ' ' + str(fil.size))

def retreivedatablock(infolder="datablock.dbb", key="",salt="salt.salt"):
    return pickle.loads(fdecryption(infolder,key,salt))

def dirdatablockandbingen(folderordir="test.txt", datablockn="datablock.dbb", binaryn="encrypted.bin", key="",salt="salt.salt",append=False):
    ##hazard checking
    if not os.path.exists(folderordir):
        raise Exception("Target directory or file doesn't exist")

    if append and not(os.path.isfile(datablockn) and os.path.isfile(binaryn)):
        raise Exception ("You are using append flag on files that might be missing")
    
    if not append and (os.path.isfile(datablockn) or os.path.isfile(binaryn)):
        raise Exception ("At least one of the specified files exist and might be subject to overwrite")

    #head tracking
    TR_HEAD = 0

    if not append:
        db = Dir("root",[],[])
    else:
        db = retreivedatablock(datablockn,key,salt)
        TR_HEAD = os.path.getsize(binaryn)

    if os.path.isfile(folderordir):
        bfilnames = [node.name for node in db.files]
        print(bfilnames)
        print(os.path.basename(folderordir))
        if os.path.basename(folderordir) in bfilnames:
            raise Exception("File overwrite hazard! Check for " + folderordir)
        else:
            with open(folderordir,"rb") as f:
                db.files.append(File(os.path.basename(folderordir),fencryption(f.read(), binaryn, key, True, salt),TR_HEAD))
    else:
        bdirnames = [node.name for node in db.dirs]
        try:
            ind = bdirnames.index(os.path.basename(folderordir))
        except ValueError:
            db.dirs.append(Dir(os.path.basename(folderordir),[],[]))
            ind = -1
        #if we are handling a directory tree it should include some files
        DIRECTORY_E = True
        #used for directory encryption append
        def dirrecc(fulldir, blockptr):
            nonlocal TR_HEAD
            nonlocal DIRECTORY_E
            
            for entry in os.scandir(fulldir):
                if entry.is_dir():
                    bdirnames = [node.name for node in blockptr.dirs]
                    try:
                        ind = bdirnames.index(entry.name) ##should throw value error if directory doesn't exist
                        dirrecc(fulldir+'\\'+entry.name, blockptr.dirs[ind]) ##just merge directory class
                    except ValueError:
                        #for some reason python assigns last used array instead of an empty array on init
                        #i swear i was about to pull my hair. don't trust python with empty array inits!
                        blockptr.dirs.append(Dir(os.path.basename(entry.name),[],[]))
                        dirrecc(fulldir+'\\'+entry.name, blockptr.dirs[-1])
                else:
                    bfilnames = [node.name for node in blockptr.files]
                    if entry.name in bfilnames:
                        logging.basicConfig(filename="hazards.log", format="%(asctime)s -> %(message)s")
                        logging.warning("Overwrite hazard! Check for " + fulldir+'\\'+entry.name)
                    else:
                        dataf = open(fulldir+'\\'+entry.name, "rb")
                        data = dataf.read()
                        dataf.close()
                        blockptr.files.append(File(os.path.basename(entry.name), fencryption(data, binaryn, key, True, salt), TR_HEAD))
                        TR_HEAD += blockptr.files[-1].size
                        if DIRECTORY_E:
                            DIRECTORY_E = False
        
        dirrecc(folderordir,db.dirs[ind])
        #given dir might have no content or dir reccursion might not create a block
        #why would you give a directory where there is nothing to encrypt?
        if DIRECTORY_E:
            raise Exception("No datablock generation! Empty directory append.")

        if append:
            db.dirs.sort(key=lambda x: x.name)
            db.files.sort(key=lambda x: x.name)

    #encrypt datablock
    fencryption(pickle.dumps(db), datablockn, key, False, salt)

if __name__ == "__main__":
    try:
        dirdatablockandbingen(folderordir="deprecated",append=True)
        #fulldecryption(retreivedatablock())
        retreivedatablock().prdir()
    except ValueError:
        print("Password is incorrect")