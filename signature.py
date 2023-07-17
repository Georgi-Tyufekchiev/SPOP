from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA384

"""
28/11/2022 11:45
Georgi Tyufekchiev
War of F(u)nctions
A 1v1 turn based game where you try to guess the other players function
This file contains the creation of signatures for files
"""

def keySetup(name):
    key = RSA.generate(2048)
    file_out = open(f"private_{name}.pem", "wb")
    file_out.write(key.export_key())
    file_out.close()

    public_key = key.publickey().export_key()
    file_out = open(f"receiver_{name}.pem", "wb")
    file_out.write(public_key)
    file_out.close()


def sign(filename, name):
    key = RSA.import_key(open(f"private_{name}.pem").read())
    signature = pkcs1_15.new(key)
    data = open(filename).read()
    hash = SHA384.new()
    hash.update(bytes(data.encode("utf8")))
    s = signature.sign(hash)
    file = open(f"signature_{name}", "wb")
    file.write(s)
    file.close()
    return s


def verify(filename, name):
    recipient_key = RSA.import_key(open(f"receiver_{name}.pem").read())
    signature = pkcs1_15.new(recipient_key)
    oldSign = open(f"signature_{name}", "rb").read()

    file = open(filename).read()
    hash = SHA384.new()
    hash.update(bytes(file.encode("utf8")))
    signature.verify(hash, oldSign)
