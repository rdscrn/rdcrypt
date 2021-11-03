import os
import sys
from cryption import *
import pickle

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

def retreivedatablock(infolder="datablock.dbb", key="1234",salt="salt"):
    return pickle.loads(fdecryption(infolder,key,salt))

def fulldecryption(datablock, key="1234", encfolder="encrypted.bin"):
    def fulldecryptionloop(blockptr,blockdir):
        for file in blockptr.files:
            with open(blockdir+"\\"+file.name, "wb") as ou:
                ou.write(fblockdecryption(file.head,file.size,encfolder,key))
        for dir in blockptr.dirs:
            os.makedirs(blockdir+"\\"+dir.name)
            fulldecryptionloop(dir,blockdir+"\\"+dir.name)
    if type(datablock) is str:
        datablock = retreivedatablock(datablock,key=key)
    curdir = datablock.name
    if os.path.exists(curdir):
        raise Exception("File already exists. Preventing overwrite...")
    os.makedirs(curdir)
    fulldecryptionloop(datablock,curdir)

def dirdatablockandbingen(folder="test", datablockn="datablock.dbb", binaryn="encrypted.bin", key="1234",salt="salt",append=False):
    #directory tree should have some files
    DIRECTORY_E = True
    if not os.path.isdir(folder):
        raise Exception("Cannot generate/append encrypted database of non directory")

    if append and not(os.path.isfile(datablockn) and os.path.isfile(binaryn)):
        raise Exception ("You are using append flag on files that might be missing")
    
    if not append and (os.path.isfile(datablockn) or os.path.isfile(binaryn)):
        raise Exception ("At least one of the specified files exist and might be subject to overwrite")

    if not append:
        db = Dir("encroot",[],[])
        TR_HEAD = 0
    else:
        db = retreivedatablock(datablockn,key,salt)
        TR_HEAD = os.path.getsize(binaryn)

    def dirrecc(fulldir, blockptr):
        nonlocal TR_HEAD
        nonlocal DIRECTORY_E
        
        for entry in os.scandir(fulldir):
            if entry.is_dir():
                bdirnames = [node.name for node in blockptr.dirs]
                try:
                    ind = bdirnames.index(entry.name) ##should throw value error if file doesn't exist
                    dirrecc(fulldir+'\\'+entry.name, blockptr.dirs[ind]) ##just merge directory class
                except ValueError:
                    #for some reason python assigns last used array instead of an empty array on init
                    #i swear i was about to pull my hair. don't trust python with empty array inits!
                    blockptr.dirs.append(Dir(os.path.basename(entry.name),[],[]))
                    dirrecc(fulldir+'\\'+entry.name, blockptr.dirs[-1])
            else:
                bfilnames = [node.name for node in blockptr.files]
                if entry.name in bfilnames:
                    print("File overwrite hazard! Check for " + fulldir+'\\'+entry.name)
                else:
                    dataf = open(fulldir+'\\'+entry.name, "rb")
                    data = dataf.read()
                    dataf.close()
                    blockptr.files.append(
                        File(os.path.basename(entry.name), 
                            fencryption(data, binaryn, key, True, salt),
                            TR_HEAD))
                    TR_HEAD += blockptr.files[-1].size
                    if DIRECTORY_E:
                        DIRECTORY_E = False
    if append:
        dirrecc(folder,db)
        db.dirs.sort(key=lambda x: x.name)
        db.files.sort(key=lambda x: x.name)
    else:
        dirrecc(folder,db)
        #given dir might have no content or dir reccursion might not create a block
        #why would you give a directory where there is nothing to encrypt?
        if DIRECTORY_E:
            raise Exception("No datablock generation! Conflicting files or empty directory append.")

    fencryption(pickle.dumps(db), datablockn, key, False, salt)

#append new encrypted block into database and update datablock base
def datablockappend(appdirfile, key="1234", olddatablock="datablock.dbb", encfolder="encrypted.bin", salt="salt"):
    try:
        db = retreivedatablock(olddatablock,key)
    except ValueError as e:
        raise e

    TR_HEAD = os.path.getsize(encfolder)
    if TR_HEAD == 0:
        raise Exception("File error")

    if not os.path.exists(appdirfile):
        raise Exception("Append file/directory doesn't exist.")
    elif os.path.isdir(appdirfile):
        dirdatablockandbingen(
            appdirfile,
            olddatablock,
            encfolder,
            key,
            salt,
            append=True)
    elif os.path.isfile(appdirfile,db):
        for a in db.files:
            if a.name == os.path.basename(appdirfile):
                raise Exception("File with same name exists. Preventing duplicate.")
        with open(appdirfile,"rb") as file:
            binsize = fencryption(file.read(),encfolder,key,True,salt)
        db.files.append(File(os.path.basename(appdirfile),binsize,TR_HEAD))
        fencryption(pickle.dumps(db),olddatablock,key,False,salt)

if __name__ == "__main__":
    try:
        fulldecryption(retreivedatablock())
    except ValueError:
        print("Password is incorrect")