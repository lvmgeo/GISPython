# -*- coding: utf-8 -*-
"""
    File and filesystem operations module
"""
import os
import shutil
from datetime import date, datetime, timedelta
import stat
import fnmatch
import SimpleFileOps

class SimpleFileOpsSafe(SimpleFileOps.SimpleFileOps):
    """Class for easing the most typical file and filesystem operations"""
    def __init__(self, _Tool):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            Tool: The 'GISTools10' object for data processing
        """
        super(SimpleFileOpsSafe, self).__init__(_Tool)

    def ClearDir(self, DirName, searchPatern = '*'): # Overriding
        """Directory cleaning automation procedure

        Args:
            self: The reserved object 'self'
            DirName: The directory to be cleaned
        """
        self.Tool.AddMessage(u"\n----------- Cleaning directory [" +  DirName + "] -------" + self.Tool.MyNow())
        self._clear_dir(DirName, searchPatern)
        self.Tool.AddMessage(u"    ... directory [" +  DirName + u"] cleaned ")

    def DelClearDir(self, DirName): # Overriding
        """Delete non-empty directory

        Args:
            self: The reserved object 'self'
            DirName: The directory to be deleted
        """
        self.Tool.AddMessage(u"\n----------- Cleaning and deleting directory [" +  DirName + "] -------" + self.Tool.MyNow())
        self._clear_dir(DirName)
        os.rmdir(DirName)
        self.Tool.AddMessage(u"    ... directory [" +  DirName + u"] deleted ")

    def BackupFiles(self, InDirName, OutDirName, D=0, Ext='*'): # Overriding
        """File archiving automation procedure

        Args:
            self: The reserved object 'self'
            InDirName: Input directory
            OutDirName: Output directory
            D: How old files to archive (number of days)
            Ext: The extension to search for ('*' - search any file)
        """
        self.Tool.AddMessage('Executing file, newer than ' +  str(D) + ' days, archiving from [' +  InDirName + '] to [' +  OutDirName + ']')
        d = date.today() - timedelta(days=D)
        d = datetime(year=d.year, month=d.month, day=d.day)
        for file in self.FindFileByDate(InDirName, Ext, d, 'Old'):
            self.BackupOneFile(file, os.path.join(OutDirName, os.path.basename(file)))

    def BackupOneFile(self, InFileName, OutDirName): # Overriding
        """Specific file archiving automation procedure

        Args:
            self: The reserved object 'self'
            InFileName: Input file
            OutDirName: Output directory
        """
        self.Tool.AddMessage("--- Archiving file [" +  InFileName + "] to [" + OutDirName + "] - " + self.Tool.MyNow())
        if os.path.exists(InFileName):
            shutil.copy(InFileName, OutDirName + '\\' + os.path.split(InFileName)[1].split(".")[-2] + "_" + self.Tool.MyNowFile() + os.path.splitext(InFileName)[1])
            self._force_remove_file_or_symlink(InFileName)
        else:
            self.Tool.AddMessage("    File " + InFileName + " does not exist ...")

    # http://stackoverflow.com/questions/1889597/deleting-directory-in-python
    def _remove_readonly(self, fn, path_, excinfo):
        """Remove read-only files and directories

        Args:
            self: The reserved object 'self'
            fn: Function for removing either a directory or a file
            path_: Path to the directory/file
        """
        if fn is os.rmdir:
            os.chmod(path_, stat.S_IWRITE)
            os.rmdir(path_)
        elif fn is os.remove:
            os.chmod(path_, stat.S_IWRITE)
            os.remove(path_)


    def _force_remove_file_or_symlink(self, path_):
        """Force remove files and symlinks

        Args:
            self: The reserved object 'self'
            path_: Path to the file/symlink
        """
        try:
            os.remove(path_)
        except OSError:
            os.chmod(path_, stat.S_IWRITE)
            os.remove(path_)


    def _is_regular_dir(self, path_):
        """Check if directory is regular directory

        Args:
            self: The reserved object 'self'
            path_: Path to the directory
        """
        try:
            mode = os.lstat(path_).st_mode
        except os.error:
            mode = 0
        return stat.S_ISDIR(mode)


    def _clear_dir(self, path_, pattern='*'):
        """Clear directory contents

        Args:
            self: The reserved object 'self'
            path_: Path to the directory
            pattern: Check if the file matches the given pattern (Default = '*'(Matches everything))
        """
        if self._is_regular_dir(path_):
            # Given path is a directory, clear its contents
            for name in [filename for filename in os.listdir(path_)  if fnmatch.fnmatch(filename, pattern)]:
                fullpath = os.path.join(path_, name)
                if self._is_regular_dir(fullpath):
                    shutil.rmtree(fullpath, onerror=self._remove_readonly)
                else:
                    self._force_remove_file_or_symlink(fullpath)
        else:
            # Given path is a file or a symlink.
            # Raise an exception here to avoid accidentally clearing the contents
            # of a symbolic linked directory.
            raise OSError("Cannot call clear_dir() on a symbolic link")
