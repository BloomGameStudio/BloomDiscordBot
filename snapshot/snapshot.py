"""
Currently we are using subprocess to run the snapshot.js file
in the snapshot directory. 

This is because there is no Python Library for Snapshot, and the JS
Library appears to utilize signing messages using EIP-712 standard which 
no library appears to exist for this in Python.

The API requires that the message is signed using EIP-712 standard. More 
information is here: 

https://snapshot.mirror.xyz/vuManI14DW8u2zhrlskndNgQcXOTbKIelQvkgmxOG2k

We could try and make this ourselves but it could be a lot of work and
I am not sure if it is worth it at the moment
"""
import subprocess

js_file_path = './snapshot/snapshot.js'

subprocess.run(['node', js_file_path])