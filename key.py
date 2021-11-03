from Crypto.Protocol.KDF import PBKDF2

def genkey(password,saltf="salt.salt"):
	f = open(saltf,"rb")
	salt = f.read()
	f.close()
	return PBKDF2(password, salt, dkLen=32)

if __name__ == "__main__":
	print(genkey("1234"))