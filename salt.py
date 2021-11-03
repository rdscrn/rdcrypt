from Crypto.Random import get_random_bytes
import os

def gensalt():
	return get_random_bytes(32)

def fileiterator(name):
	if not isinstance(name, str) or not name:
		raise Exception("Filename must be specified")
	itn = 0
	nameo = name
	while os.path.exists(nameo):
		nameo = name+str(itn)
		itn += 1
	return nameo

def gensaltfile(name):
	f = open(fileiterator(name),"ab")
	f.write(gensalt())
	f.close()

if __name__ == "__main__":
	gensaltfile("salt")