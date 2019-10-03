import hashlib
import binascii

def dblShaFlip(header):
    first_hash = hashlib.sha256(binascii.unhexlify(header)).hexdigest()
    second_hash = hashlib.sha256(binascii.unhexlify(first_hash)).hexdigest()
    return flipBytes(second_hash)

def flipBytes(b):
    byteSize = 2
    chunks = [ b[i:i+byteSize] for i in range(0, len(b), byteSize) ]
    reversed_chunks = chunks[::-1]
    return ('').join(reversed_chunks)

def double_sha256(data):
    hash = hashlib.sha256(binascii.unhexlify(data)).hexdigest()
    hash2 = hashlib.sha256(binascii.unhexlify(hash)).hexdigest()
    return hash2


def extractPathFromMerkleBlock(merkleBlock):
    nHashes = merkleBlock[168:][:2]
    path = ""
    tmpData = merkleBlock[170:]
    for i in range(1,nHashes+1):
        path =+ tmpData[i*64:]
    return path


