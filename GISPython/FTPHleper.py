# -*- coding: utf-8 -*-
"""
     FTP operations module
"""

import datetime
import os
import traceback
import sys
import MyError

class FTPFile:
    """Class for describing the FTP file"""

    def __init__(self, file, date, size):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            file: Filename
            date: File date
            size: File size
        """
        self.file = file
        self.date = date
        self.size = size

class FTPHleper:
    """Class for easing the FTP operations"""

    def __init__(self, FTPHost, FTPUser, FTPPwd, FTPDir=None):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            FTPHost: FTP server
            FTPUser: FTP username
            FTPPwd: FTP user password
        """
        import ftplib

        try:
            self.ftp = ftplib.FTP(FTPHost, FTPUser, FTPPwd)
            if FTPDir == None:
                self.ftp.cwd('/')
            else:
                self.ftp.cwd(FTPDir)
        except Exception, e:

            tb = sys.exc_info()
            txt = "Line %i" % tb[2].tb_lineno + unicode(traceback.format_exc(), errors='ignore')
            raise MyError.MyError(u"Error connecting to ftp: " + FTPHost + u'\n Error output: \n\n' + txt)


    def list_files(self):
        """Procedure to retrieve a file description in the specific connection directory

        Args:
            self: The reserved object 'self'
        """
        self.files = []
        self.ftp.dir(self.dir_callback)
        return self.files

    def get_file_date(self, fileName):
        """Determines the ftp file modification date

        Args:
            self: The reserved object 'self'
            fileName: Ftp file name
        """
        modifiedTime = self.ftp.sendcmd('MDTM ' + fileName)
        modifiedTime = self.ftp.sendcmd('MDTM ' + fileName)
        return datetime.datetime.strptime(modifiedTime[4:], "%Y%m%d%H%M%S")

    def get_file_size(self, fileName):
        """Determines the ftp file size

        Args:
            self: The reserved object 'self'
            fileName: Ftp file name
        """
        size = self.ftp.sendcmd('SIZE ' + fileName)
        size = self.ftp.sendcmd('SIZE ' + fileName)
        return int(size[4:])

    def get_file(self, filename, savePath):
        """Retrieves the file from the FTP server

        Args:
            self: The reserved object 'self'
            filename: Ftp file name
        """
        # Open the file for writing in binary mode
        print 'Opening local file ' + savePath
        file = open(savePath, 'wb')
        fSize = [0, 0]

        # Download the file a chunk at a time
        # Each chunk is sent to handleDownload
        # We append the chunk to the file and then print a '.' for progress
        # RETR is an FTP command

        def download_file_callback(data):
            """Download file callback"""
            file.write(data)
            fSize[0] += len(data)
            fSize[1] += len(data)
            if fSize[1] >= 10485760:
                file.flush()
                print 'Downloaded ' + str(fSize[0]/1048576) + ' MB'
                fSize[1] = 0

        print 'Getting ' + savePath
        self.ftp.retrbinary('RETR %s' % filename, download_file_callback, 4096)

        # Clean up time
        print 'Closing file ' + savePath
        file.close()

    def upload_file(self, fileName, filePath):
        """Uploads the binary file, using FTP

        Args:
            self: The reserved object 'self'
            filePath: Uploadable file local path
            fileName: Uploadable file name
        """
        uploadFile = open(os.path.join(filePath, fileName), 'rb')
        # Store a file in binary transfer mode
        self.ftp.storbinary('STOR ' + fileName, uploadFile)
        # close file
        uploadFile.close()

    def delete_file(self, fileName):
        """Deletes the file from the FTP server

        Args:
            self: The reserved object 'self'
            fileName: Name of the file to delete
        """
        self.ftp.delete(fileName)

    def dir_callback(self, line):
        """Processes callback from the procedure 'list_files'

        Args:
            self: The reserved object 'self'
            line: Row with the FTP file description
        """
        bits = line.split()

        if 'd' not in bits[0]:
            fFile = FTPFile(bits[-1], self.get_file_date(bits[-1]), self.get_file_size(bits[-1]))
            self.files.append(fFile)
