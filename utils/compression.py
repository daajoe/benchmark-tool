#
# HANDLE COMPRESSION
# Taken from: SO:#13044562
#
#

from itertools import imap

class CompressedFile (object):
    magic = None
    file_type = None
    mime_type = None
    proper_extension = None

    def __init__(self, f):
        # f is an open file or file like object
        self.f = f
        self.accessor = self.open()

    @classmethod
    def is_magic(self, data, filename):
        print filename
        if data.startswith(self.magic):
            return True
        elif any(imap(lambda x: filename.endswith(x), self.ext)):
            return True
        else:
            return False

    def open(self):
        return None

import zipfile

class ZIPFile (CompressedFile):
  magic = '\x50\x4b\x03\x04'
  file_type = 'zip'
  mime_type = 'compressed/zip'
  ext = 'zip'
  
  def open(self):
    return zipfile.ZipFile(self.f.name)
  
import bz2

class BZ2File (CompressedFile):
  magic = '\x42\x5a\x68'
  file_type = 'bz2'
  mime_type = 'compressed/bz2'
  ext = 'bz2'
  
  def open(self):
    return bz2.BZ2File(self.f.name)

import gzip

class GZFile (CompressedFile):
  magic = '\x1f\x8b\x08'
  file_type = 'gz'
  mime_type = 'compressed/gz'
  ext = 'gz'
  
  def open(self):
    return gzip.GzipFile(self.f.name)


import backports.lzma as xz

class XZ(CompressedFile):
  #magic = 'FD 37 7A 58 5A 00' #\x1f\x8b\x08
  magic = '\x5a\x57\x53'
  magic = '\xFD\x37\x7A\x58\x00'
  magix = '\x37\x7a\xbc\xaf\x27\x1c'
  file_type = 'lzma'
  mime_type = 'application/x-lzma'
  ext = ['xy', 'lzma']
  
  def open(self):
    return xz.LZMAFile(self.f.name)


# factory function to create a suitable instance for accessing files
def get_compressed_file(filename):
    print filename
    with file(filename, 'rb') as f:
        start_of_file = f.read(1024)
        f.seek(0)
        for cls in (ZIPFile, BZ2File, GZFile, XZ):
            if cls.is_magic(start_of_file, filename):
                return cls(f)
      
    raise IOError("Unknown mime type.")
