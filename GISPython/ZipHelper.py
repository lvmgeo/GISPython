# -*- coding: utf-8 -*-
"""
     Zip file operations module
"""
import os
import zipfile

class ZipHelper:
    """Class for easing the Zip file operations"""

    def __init__(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """

    def CompressFile(self, filePath, zipFileName):
        """Compress file

        Args:
            self: The reserved object 'self'
            filePath: Archivable file path + name
            zipFileName: New Zip file path + name
        """
        zfile = zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_DEFLATED)
        zfile.write(filePath, arcname=zfile.write(filePath, arcname=os.path.basename(filePath)))
        zfile.close()

    def CompressFileList(self, filePathList, zipFileName, base_dir=None, append=False):
        """Zip all files in the list

        Args:
            self: The reserved object 'self'
            filePathList: List of archivable file paths + names
            zipFileName: New Zip file path + name
            base_dir: dase dir to strip from paths in file lists
            append (Bool): (Optional) True if Zip exists and data is appended to it
        """
        if append:
            zfile = zipfile.ZipFile(zipFileName, 'a', zipfile.ZIP_DEFLATED, allowZip64=True)
        else:
            zfile = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
        for filePath in filePathList:
            if base_dir is None:
                arc_name = os.path.basename(filePath)
            else:
                arc_name = _ireplace(base_dir, '', filePath)
            zfile.write(filePath, arcname=arc_name)
        zfile.close()

    def CompressDir(self, dirPath, zipFileName, excludeExt=[], append=False, start_path_in_zip=''):
        """Zip all files in the directory

        Args:
            self: The reserved object 'self'
            zipFileName (string): New Zip file path + name
            dirPath (string): Directory which contains archivable files
            excludeExt (list): File extensions not to include in the archive
            append (Bool): (Optional) True if Zip exists and data is appended to it
            start_path_in_zip (string): (Optional) used to specify subfolder in zipfile in with data vill be written
        """
        if append:
            zfile = zipfile.ZipFile(zipFileName, 'a', zipfile.ZIP_DEFLATED, allowZip64=True)
        else:
            zfile = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
        for root, dirs, files in os.walk(dirPath):
            for file_path in files:
                do_compress = True
                for ext in excludeExt:
                    if file_path.endswith(ext):
                        do_compress = False
                if do_compress:
                    zfile.write(os.path.join(root, file_path), arcname=os.path.join(root, file_path).replace(dirPath, start_path_in_zip))
        zfile.close()

    def ExtractZipFile(self, zipFileName, destPath):
        """Extracts the compressed file

        Args:
            self: The reserved object 'self'
            zipFileName: Extractable file full path + name
            destPath: Destination path in which to extract the files
        """
        zfile = zipfile.ZipFile(zipFileName)
        zfile.extractall(destPath)
        zfile.close()

def _ireplace(old, new, text):
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(new)
    return text
