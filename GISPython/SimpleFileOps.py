# -*- coding: utf-8 -*-
"""
    File and filesystem operations module
"""
import os
import shutil
import unicodedata
import codecs
from datetime import datetime
import simplejson as json

class SimpleFileOps(object):
    """Class for easing typical file and filesystem operations"""
    def __init__(self, _Tool):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            Tool: The GISTools10 object for data processing
        """
        self.Tool = _Tool

    def ClearDir(self, DirName, searchPatern='*'): # Overriding
        """Directory cleaning automation procedure

        Args:
            self: The reserved object 'self'
            DirName: The directory to be cleaned
        """
        self.Tool.AddMessage(u"\n----------- Cleaning directory [" +  DirName + u"] searching: {" + searchPatern + "} -------" + self.Tool.MyNow())
        self.Tool.RunPS("ClearDir", '"' + self.Tool.CorrectStr(DirName) + '" ' + searchPatern, os.path.dirname(__file__))

    def DelClearDir(self, DirName): # Overriding
        """Delete non-empty directory

        Args:
            self: The reserved object 'self'
            DirName: The directory to be deleted
        """
        self.Tool.AddMessage(u"\n----------- Cleaning and deleting directory [" +  DirName + "] -------" + self.Tool.MyNow())
        self.Tool.RunPS("ClearDir", '"' + self.Tool.CorrectStr(DirName) + '" ' + searchPatern, os.path.dirname(__file__))
        os.rmdir(DirName)
        self.Tool.AddMessage(u"    ... directory [" +  DirName + u"] deleted ")

    def BackupFiles(self, InDirName, OutDirName, D): # Overriding
        """File archiving automation procedure (Overriding)

        Args:
            self: The reserved object 'self'
            InDirName: Input directory
            OutDirName: Output directory
            D: How old files to archive (number of days)
        """
        self.Tool.RunPS("BackupOldFiles", '"' + self.Tool.CorrectStr(InDirName) + '" "' + self.Tool.CorrectStr(OutDirName) + '" ' + str(D), os.path.dirname(__file__))

    def GetLog(self, server, EventLogOutputDir, D): # NoneOverriding
        """File archiving automation procedure (None overriding)

        Args:
            self: The reserved object 'self'
            server: Server which eventlog backup to create
            EventLogOutputDir: Event log output directory
            D: How old files to archive (number of days)
        """
        self.Tool.RunPS("GetLog", '"' + server + '" "' + self.Tool.CorrectStr(EventLogOutputDir) + '" '+ str(D), os.path.dirname(__file__))

    def BackupOneFile(self, InFileName, OutDirName): # Overriding
        """Specific file archiving automation procedure

        Args:
            self: The reserved object 'self'
            InFileName: Input file
            OutDirName: Output directory
        """
        self.Tool.AddMessage("")
        self.Tool.AddMessage("--- Archiving file " +  InFileName + " to " + OutDirName + " - " + self.Tool.MyNow())
        if os.path.exists(InFileName):
            shutil.move(InFileName, OutDirName + '\\' + os.path.split(InFileName)[1].split(".")[-2] + "_" + self.Tool.MyNowFile() + os.path.splitext(InFileName)[1])
        else:
            self.Tool.AddMessage("    File " + InFileName + ' does not exist ...')

    def CheckCreateDir(self, OutDirName):
        """Automation procedure which creates directory, in case it doesn't exist

        Args:
            self: The reserved object 'self'
            OutDirName: Output directory
        """
        if not os.path.exists(OutDirName):
            os.makedirs(OutDirName)

    def GetSafeName(self, text, substituteChar='_', aditionalScaryChars='', aditionalSpaceChars='', noDotsInName=False):
        """Modifies the text for use in the filesystem

        Args:
            self: The reserved object 'self'
            text: Text string which will be transformed
            substituteChar: Character to substitute the whitespace
            aditionalScaryChars: Additional characters to eliminate
            aditionalSpaceChars: Additional characters to replace
            noDotsInName: Forbid dots in filename (except the file extension seperator) (Default = False)

        Returns:
            * Modified text as string
        """
        if type(text) is unicode:
            text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
        checkChars = ''.join(set(r'[]/\;,><&*:%=+@!#^()|?^-' + aditionalScaryChars))
        for c in checkChars:
            text = text.replace(c, '')
        checkSpaceChars = ''.join(set(' ' + aditionalSpaceChars))
        for c in checkSpaceChars:
            text = text.replace(c, substituteChar)
        if noDotsInName:
            lastDot = text.rfind('.')
            if lastDot != -1:
                text = (text[:lastDot]).replace('.', substituteChar) + text[lastDot:]
        while text.find(substituteChar+substituteChar) > -1:
            text = text.replace(substituteChar+substituteChar, substituteChar)
        return text

    def FindNewestFile(self, Dir, Ext='*'):
        """Finds the newest file in the directory

        Args:
            self: The reserved object 'self'
            Dir: The directory in which to look for the file
            Ext: The extension to search for ('*' - search any file)
        """
        if not Ext == '*':
            dated_files = [(os.path.getmtime(Dir + "\\" + fn), os.path.basename(Dir + "\\" + fn))
                           for fn in os.listdir(Dir)
                          ]
        else:
            dated_files = [(os.path.getmtime(Dir + "\\" + fn), os.path.basename(Dir + "\\" + fn))
                           for fn in os.listdir(Dir)
                           if fn.lower().endswith('.' + (Ext.lower()))
                          ]
        dated_files.sort()
        dated_files.reverse()
        newest = dated_files[0][1]
        return Dir + "\\" + newest

    def FindFileByDate(self, Dir, Ext='*', Date=datetime.now(), Mode='New'):
        """Find files in the given directory which are newer than the given date

        Args:
            self: The reserved object 'self'
            Dir: The directory in which to look for the file
            Ext: The extension to search for ('*' - search any file)
            Date: Find files newer than given date
            Mode: File searching modes: New - search newer files; Old - search older files (Default = New)
        """
        if Ext == '*':
            dated_files = [Dir + "\\" + fn
                           for fn in os.listdir(Dir)
                           if ((Mode == 'New' and datetime.fromtimestamp(os.path.getmtime(Dir + "\\" + fn)) >= Date) or
                               (Mode == 'Old' and datetime.fromtimestamp(os.path.getmtime(Dir + "\\" + fn)) <= Date))
                          ]
        else:
            dated_files = [Dir + "\\" + fn
                           for fn in os.listdir(Dir)
                           if ((Mode == 'New' and datetime.fromtimestamp(os.path.getmtime(Dir + "\\" + fn)) >= Date) or
                               (Mode == 'Old' and datetime.fromtimestamp(os.path.getmtime(Dir + "\\" + fn)) <= Date))
                           and fn.lower().endswith('.' + (Ext.lower()))
                          ]
        dated_files.sort()
        return dated_files

    def FindFile(self, Dir, Ext):
        """Finds files in the directory

        Args:
            self: The reserved object 'self'
            Dir: The directory in which to look for the file
            Ext: The extension to search for
        """
        dated_files = [Dir + "\\" + fn
                       for fn in os.listdir(Dir) if fn.lower().endswith('.' + (Ext.lower()))]
        dated_files.sort()
        return dated_files

    def FindDirectory(self, Dir, Searchpattern='*'):
        """Find subdirectories in the given directory

        Args:
            self: The reserved object 'self'
            Dir: The directory in which to look for subdirectories
            Searchpattern: Searching condition
        """
        if Searchpattern == '*':
            dirs = [fn for fn in os.listdir(Dir) if os.path.isdir(fn)]
        else:
            dirs = [fn for fn in os.listdir(Dir) if os.path.isdir(fn)
                    and not fn.lower().find(Searchpattern.lower()) == -1]
        dirs.sort()
        return dirs

    def FindFileRecursive(self, Dir, Ext):
        """Find files by extension

        Args:
            self: The reserved object 'self'
            Dir: The directory in which to look for the file
            Ext: The extension to search for
        """
        dated_files = []
        for root, dirnames, filenames in os.walk(Dir):
            for filename in filenames:
                if filename.lower().endswith('.' + (Ext.lower())):
                    dated_files.append(os.path.join(root, filename))
        dated_files.sort()
        return dated_files

    def CopyAllFilesInDir(self, SourceDir, DestDir, Searchpattern='*', Ignorepattern=None):
        """Copy entire directory tree from one directory to another

        Args:
            self: The reserved object 'self'
            SourceDir: Source directory
            DestDir: Destination directory
            Searchpattern: Searching condition
        """
        if not os.path.exists(DestDir):
            os.makedirs(DestDir)

        if Searchpattern == '*' and Ignorepattern==None:
            foundfiles = [fn for fn in os.listdir(SourceDir)]
        elif Searchpattern != '*' and Ignorepattern==None:
            foundfiles = [fn for fn in os.listdir(SourceDir) if not fn.lower().find(Searchpattern.lower()) == -1]
        elif Searchpattern == '*' and Ignorepattern!=None:
            foundfiles = [fn for fn in os.listdir(SourceDir) if fn.lower().find(Ignorepattern.lower()) == -1]
        elif Searchpattern != '*' and Ignorepattern!=None:
            foundfiles = [fn for fn in os.listdir(SourceDir) if not fn.lower().find(Searchpattern.lower()) == -1 and fn.lower().find(Ignorepattern.lower()) == -1]
        foundfiles.sort()

        for item in foundfiles:
            s = os.path.join(SourceDir, item)
            d = os.path.join(DestDir, item)
            if os.path.isdir(s):
                self.CopyAllFilesInDir(s, d, False, None)
            else:
                shutil.copy2(s, d)

    def printFile(self, filePath):
        """Print file content to the screen

        Args:
            self: The reserved object 'self'
            filePath: File to print
        """
        with codecs.open(filePath, 'r', 'utf8') as fin:
            self.Tool.AddMessage(fin.read())

    def GetfileNameWithDate(self, file):
        """Add a date at the end of the filename

        Args:
            self: The reserved object 'self'
            file: Full path to the file to add the date
        """
        dirname = os.path.dirname(file)
        filename = ('.').join(file.split('.')[:-1])
        fileext = ('.').join(file.split('.')[-1:])

        return os.path.join(dirname, filename + '_' + self.Tool.MyNowFileSafe() + '.' + fileext)

class LockSubprocess(object):
    """Class that provides directory locking control and processing"""
    def __init__(self, Tool, Dir, processName):
        """Class initialization procedure
        Args:
            self: The reserved object 'self'
            Tool: Reference to the GISTools10 object
            Dir: Working directory
            processName: Name of the process
        """
        self.StartTime = datetime.now()
        self.Tool = Tool
        self.Dir = Dir
        self.processName = processName
        self.results = LockResults(processName)
        self.lockFileName = os.path.join(self.Dir, 'gispython.{0}.lock'.format(self.processName))

    def __enter__(self):
        """With statement opening procedure
        Args:
            self: The reserved object 'self'
        Returns:
            LockResults with status:
                Locked - The file is locked by another process;
                DoneBefore -  Process is already done;
                NoDir - Directory not found;
                Running - Process is running;
        """
        # Check if directory exists
        if os.path.exists(self.Dir):
            if os.path.exists(self.lockFileName) and os.path.isfile(self.lockFileName):
                try:
                    self.f = codecs.open(self.lockFileName, 'r+', 'utf-8')
                    self.readJson()
                except:
                    self.results.status = "Locked"
                    return self.results
                if self.J['status'] == 'Running':
                    self.results.status = "Locked"
                    return self.results
                if self.J['status'] == 'Done':
                    self.results.status = "DoneBefore"
                    return self.results
                else:
                    self.results.status = "Running"
                    self.writeJson()
            else:
                self.f = codecs.open(self.lockFileName, 'w', 'utf-8')
                self.results.status = "Running"
                self.writeJson()
        else:
            self.results.status = "NoDir"
        return self.results

    def __exit__(self, type, value, traceback):
        """With statement closing procedure
        Args:
            self: The reserved object 'self'
        """
        if self.results.status == "Running":
            self.results.status = "Done"
            if hasattr(self, 'f'):
                self.f = codecs.open(self.lockFileName, 'w', 'utf-8')
                self.writeJson()
        if hasattr(self, 'f'):
            self.f.close()

    def readJson(self):
        """Get the data from the lock file
        Args:
            self: The reserved object 'self'
        """

        JsonString = self.f.read()
        try:
            self.J = json.loads(JsonString)
        except:
            self.J = {'status':'Ok'}

    def writeJson(self):
        """Save parameters in the file
        Args:
            self: The reserved object 'self'
        """
        rezult = {'status': self.results.status,
                  'processName':self.results.processName,
                  'processdate': str(self.results.processdate)}
        JsonString = json.dumps(rezult, sort_keys=True, indent=4 * ' ')
        self.f.truncate()
        self.f.write(JsonString)
        self.f.flush()

class LockResults(object):
    """Class for saving the data processing results (for LockSubprocess)"""

    def __init__(self, processName):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            processName: Name of process
        """
        self.status = "Running"
        self.processdate = datetime.now()
        self.processName = processName

    def GetStatusTxt(self):
        """Get status description

        Args:
            self: The reserved object 'self'
        """
        if self.status == "Running":
            return u'Process execution is running'
        if self.status == "Locked":
            return u'This process cannot be continued, because another process is already running'
        if self.status == "DoneBefore":
            return u'Process is already done'
        if self.status == "NoDir":
            return u'Corresponding directory not found'
