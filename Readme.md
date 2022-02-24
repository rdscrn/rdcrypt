# redcrypt

Appendable, directory-indexed file encryption system. Using PyCryptodome chipher block chain and tkinter graphical interface.

This program creates an encrypted directory class and an appendable encrypted binary to store your password protected files. Good for encrypting large, growing but private directory structures.

Basically:
* Generate a salt file (don't lose it or change it after you encrypt your files)
* Generate an encrypted file structure (like database.dbb) and the encrypted binary data (like encrypted.bin) with given files/directory and user defined password (using only salt file is also optional but password is recommended for extra security)
* After you encrypted your data, use the same database, binary, salt and password to decrypt the file structure and indexed files. Selecting files or directories on the tree list will extract them on the designated folder
* With the same files and password, you can also add to the existing database, directory contents and data will be appended. Existing directory structures will also be expanded if new items exist in the same directory structures.

It is much faster than rar because we don't decrypt the whole database all over again

File/directory deletion is not implemented. The intention is creating append only databases.

[Download the lastest WIN build from here](https://github.com/rdscrn/redcrypt/releases/download/v1.1/redcrypt.v1_1.exe)
