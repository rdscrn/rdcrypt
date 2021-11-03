Appendable, directory-indexed file encryption system. Using PyCryptodome chipher block chain and tkinter graphical interface.

This program creates an encrypted directory class and an appandable encrypted binary to store your password protected files. Good for encrypting large, growing but private directory structures.

Basically:
-Generate a salt file (don't lose it or change it after you encrypt your files)
-Generate an encrypted file structure (like database.dbb) and the encrypted binary data (like encrypted.bin) with given files/directory and user defined password (using only salt file is also optional but password is recommended for extra security)
-After you encrypted your data, use the salt and password to decrypt the file structure. Double clicking a file on the tree list will extract file on the executable working folder (directory decryption will be implemented later)
-With the same files and password, you can also add to the existing database directory contents and data will be appended. It is much faster than rar because we don't decrypt the whole database all over again

It is not possible to remove files. But we are not aiming for that anyway.
