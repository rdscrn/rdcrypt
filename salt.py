from Crypto.Random import get_random_bytes
import os

def gensalt():
    return get_random_bytes(32)

def fileiterator(name):
    if not isinstance(name, str) or not name:
        raise Exception("Filename must be specified")
    itn = 0
    orname = os.path.splitext(name)
    while os.path.exists(name):
        name = orname[0]+str(itn)+orname[1]
        itn += 1
    return name

def gensaltfile(name):
    rn = fileiterator(name)
    with open(rn,"ab") as f:
        f.write(gensalt())
    return rn

if __name__ == "__main__":
    gensaltfile("salt.salt")