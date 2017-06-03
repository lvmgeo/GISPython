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

    def CompressFileList(self, filePathList, zipFileName):
        """Zip all files in the list

        Args:
            self: The reserved object 'self'
            filePathList: List of archivable file paths + names
            zipFileName: New Zip file path + name
        """
        zfile = zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_DEFLATED)
        for filePath in filePathList:
            zfile.write(filePath, arcname=os.path.basename(filePath))
        zfile.close()

    def CompressDir(self, dirPath, zipFileName, excludeExt=[]):
        """Zip all files in the directory

        Args:
            self: The reserved object 'self'
            zipFileName: New Zip file path + name
            dirPath: Directory which contains archivable files
            excludeExt: File extensions not to include in the archive
        """
        zfile = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(dirPath):
            for filePath in files:
                doCompress = True
                for ext in excludeExt:
                    if filePath.endswith(ext):
                        doCompress = False
                if doCompress:
                    zfile.write(os.path.join(root, filePath), arcname=os.path.basename(filePath))
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
