from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import os
import sys
from key import genkey


def fencryption(data, output_file = 'encrypted.bin', key = "1234", append = False, salt="salt"):
	key = genkey(key,salt)
	cipher = AES.new(key, AES.MODE_CBC)
	ciphered_data = cipher.encrypt(pad(data, AES.block_size))
	if append:
		file_out = open(output_file, "ab")
	else:
		file_out = open(output_file, "wb")
	file_out.write(cipher.iv)
	file_out.write(ciphered_data)
	file_out.close()

	return sys.getsizeof(ciphered_data)-16-1

def fdecryption(input_file = 'encrypted.bin', key = "1234", salt="salt"):
	key = genkey(key,salt)

	file_in = open(input_file, "rb")
	iv = file_in.read(16)
	ciphered_data = file_in.read()
	file_in.close()
	cipher = AES.new(key, AES.MODE_CBC, iv=iv)
	return unpad(cipher.decrypt(ciphered_data), AES.block_size)

def fblockdecryption(head=0, block=None,input_file = 'encrypted.bin', key = "1234", salt="salt"):
	if block is None:
		raise Exception("Datalength must be specified")
	key = genkey(key, salt)

	with open(input_file, "rb") as file_in:
		file_in.seek(head)
		iv = file_in.read(16)
		ciphered_data = file_in.read(block-16)

	cipher = AES.new(key, AES.MODE_CBC, iv=iv)
	return unpad(cipher.decrypt(ciphered_data), AES.block_size)

if __name__ == "__main__":
	"""
	with open("a\\sdfsdf.txt", "rb") as file:
		fencryption(file.read())
	"""
	with open("out.txt", "wb") as file:
		file.write(fblockdecryption(32,48))