# -*- coding: utf-8 -*-
"""Base class for GISPython Tool object
"""

import os
import datetime
import sys
import codecs
import subprocess
import shlex
import shutil
import locale
import time
import string
import unicodedata
import uuid
from multiprocessing import Process, Queue

class GISPythonToolBase(object):
    def __init__(self, ToolName, Params):
        self.ExecutePatch = os.path.dirname(os.path.realpath(__file__))
        self.Pr = Params
        self.StartTime = datetime.datetime.now()
        self.ToolName = ToolName
        self.OutputStr = u''
        self.OutputErrStr = u''
        self.State = "Started"
        
        if hasattr(Params, 'encodingPrimary'):
            UnicodeWriter = codecs.getwriter(Params.encodingPrimary)
            sys.stdout = UnicodeWriter(sys.stdout)

    def MyEnd(self):
        """End of the process

        Args:
            self: The reserved object 'self'
        """
        self.AddMessage(u'End tool ' + self.ToolName + u' execution ' + self.MyNow())
        TD = datetime.datetime.now()- self.StartTime
        self.AddMessage(u'      ...Tool execution time: ' + str(TD))
        self.State = "Done"

    def MyDispose(self):
        """Disposal of the class

        Args:
            self: The reserved object 'self'
        """
        if self.State == "Started":
            self.MyEnd()
        self.State = "Disposed"

    def AddMessage(self, strMessage, newline=True):
        """Procedure for a message output (screen, logfile and if necessary e-mail)

        Args:
            self: The reserved object 'self'
            strMessage: Output message text
            newline: Flag that marks that the output must be continued in a new line
        """
        if strMessage == None:
            strMessage = ''
        if not isinstance(strMessage, unicode):
            if not isinstance(strMessage, str):
                strMessage = str(strMessage)
        if strMessage[-1:] == '\n':
            strMessage = strMessage[0:-1]

        print strMessage

        self.OutputStr += strMessage
        if newline == True:
            self.OutputStr += '\n'

    def AddError(self, strMessage, newline=True):
        """Procedure for the GP object error message output (screen, logfile and if necessary e-mail)

        Args:
            self: The reserved object 'self'
            strMessage: Output message text
        """
        if strMessage == None:
            strMessage = ''
        if not isinstance(strMessage, unicode):
            if not isinstance(strMessage, str):
                strMessage = str(strMessage)
        if strMessage[-1:] == '\n':
            strMessage = strMessage[0:-1]

        self.AddMessage('ERROR> ' + strMessage, newline)

        self.OutputErrStr += strMessage
        if newline == True:
            self.OutputErrStr += '\n'
        
    def AddWarning(self, strMessage, newline=True):
        """Procedure for the GP object warning message output (screen, logfile and if necessary e-mail)

        Args:
            self: The reserved object 'self'
            strMessage: Output message text
        """
        if strMessage == None:
            strMessage = ''
        if not isinstance(strMessage, unicode):
            if not isinstance(strMessage, str):
                strMessage = str(strMessage)
        if strMessage[-1:] == '\n':
            strMessage = strMessage[0:-1]

        self.AddMessage('Warning> ' + strMessage, newline)

        self.OutputErrStr += strMessage
        if newline == True:
            self.OutputErrStr += '\n'

    def _tryCovertStringEncoding(self, txt):
        """Function for working with strings in diferent encodings. Converts string from input to string in correct encoding.

        Args:
            self: The reserved object 'self'
            txt: String to be converted

        Returns:
            converted string
        """
        if isinstance(txt, str):
            try:
                txt = txt.decode(self.Pr.encodingPrimary, errors='strict')
            except Exception:
                try:
                    txt = txt.decode(self.Pr.encodingSecondary, errors='strict')
                except Exception:
                    try:
                        txt = txt.decode('utf-8', errors='strict')
                    except Exception:
                        txt = txt.decode(self.Pr.encodingPrimary, errors='replace')
        return txt

    def CorrectStr(self, Str):
        """Function doubles symbol '\' in path for some external execution compatibility
        Args:
            self: The reserved object 'self'
            Str: Input string

        Returns:
            string
        """
        return Str.replace('\\', '\\\\')

    def AchiveFiles(self, Dir, AchiveDir, FileName, PrintOut=True):
        """Function moves log files to the archive

        Args:
            self: The reserved object 'self'
            Dir: Directory from which to archive
            AchiveDir: Archive directory
            FileName: Parameter for searching a file (full or partial filename)
        """
        # Check if Archive directory exists
        if os.path.exists(AchiveDir):
            names = os.listdir(Dir)
            for name in names:
                if name.lower().find(FileName.lower()) == 0:
                    if PrintOut:
                        print("        move: "  + Dir + "\\" + name + " -> " + AchiveDir + "\\" + name + "\n")
                    try:
                        shutil.move(Dir + "\\" + name, AchiveDir + "\\" + name)
                    except:
                        print("        archiving failed : "  + Dir + "\\" + name + " -> " + AchiveDir + "\\" + name + "\n")

    def MyNowFile(self):
        """Function returns formatted date for the filename output

        Args:
            self: The reserved object 'self'

        Returns:
            Date, formatted as text
        """
        return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H-%M-%S")

    def MyNowOracle(self):
        """Function returns formatted date for the data selection in SQL

        Args:
            self: The reserved object 'self'

        Returns:
            Date, formatted as text
        """
        return "TO_DATE('" + datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S") + "', 'YYYY-MM-DD HH24:MI:SS')"

    def MyNowFileSafe(self):
        """Function returns formatted date for the filename output (additional compatibility)

        Args:
            self: The reserved object 'self'

        Returns:
            Date, formatted as text
        """
        return datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")

    def MyNow(self):
        """Function returns formatted date for the output

        Args:
            self: The reserved object 'self'

        Returns:
            Date, formatted as text
        """
        return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")

    def MyNowUTC(self):
        """Function returns formatted date for the UTC date output

        Args:
            self: The reserved object 'self'

        Returns:
            Date, formatted as text
        """
        return datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S")

    def MyNowForParam(self, minusdays=0, includeTime = False):
        """Function returns formatted date (date now) for the GEO parameter processing

        Args:
            self: The reserved object 'self'
            minusdays: Number of days to subtract from today
            includeTime: Include time in param (True/False)

        Returns:
            Date, formatted as text
        """
        if includeTime:
            DD = datetime.timedelta(days=minusdays)
            return datetime.datetime.strftime((datetime.datetime.now() - DD), "%Y-%m-%d %H:%M:%S")
        else:
            DD = datetime.timedelta(days=minusdays)
            return datetime.datetime.strftime((datetime.datetime.now() - DD), "%Y-%m-%d")

    def MyDateFromParam(self, dateString, includeTime = False):
        """Function converts date written in the parameter file to a date object

        Args:
            self: The reserved object 'self'
            includeTime: Include time in param (True/False)
        """
        if includeTime:
            return datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S")
        else:
            return datetime.datetime.strptime(dateString, "%Y-%m-%d")

    def MyDateForParam(self, paramStr, includeTime = False):
        """Function returns date from GEO parameter processing saved string

        Args:
            self: The reserved object 'self'
            paramStr: Parameter value as text
            includeTime: Include time in param (True/False)

        Returns:
            datetime
        """
        if includeTime:
            return datetime.datetime.strptime(paramStr, "%Y-%m-%d %H:%M:%S")
        else:
            return datetime.datetime.strptime(paramStr, "%Y-%m-%d")

    def _runProcess(self, exe, noErr=False, Detached=False, Silent=False, hidenStrings = []):
        """Shell command execution support function (see the runShell function)

        Args:
            self: The reserved object 'self'
            exe: Executable command

        Return:
            stdoutdata
        """
        lines = list()
        if Detached == True:
            DETACHED_PROCESS = 0x00000010
            p = subprocess.Popen(exe, creationflags=DETACHED_PROCESS, stdout=None, stderr=None, shell=True, universal_newlines=True, close_fds=True) #, env={'LANG':'C'})
        else:
            p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True) #, env={'LANG':'C'})
            while True:
                retcode = p.poll() #returns None while subprocess is running
                str = p.stdout.readline()
                for hideString in hidenStrings:
                    str = str.replace(hideString, '*' * len(hideString))
                if str != '' and Silent != True:
                    self.AddMessage(u'>>>>' + self._tryCovertStringEncoding(str), True)
                lines.append(str)
                if retcode is not None:
                    break
            errlines = p.stderr.readlines()
            if not errlines == None:
                for str in errlines:
                    line = self._tryCovertStringEncoding(str)
                    for hideString in hidenStrings:
                        line = line.replace(hideString, '*' * len(hideString))
                    if line != '':
                        if noErr == False:
                            self.AddError('>>>>' + line, True)
                        else:
                            self.AddMessage('>>>>' + line, True)
        return lines

    def runShell(self, exe, noErr=False, ErrorStrings=['ERROR', 'FAILED', u'KĻŪDA', 'EXCEPTION', 'ORA-'], Detached=False, Silent=False, hidenStrings = []):
        """Shell command execution procedure. It can detect errors in execution and can output results to screen.

        Args:
            self: The reserved object 'self'
            exe: Executable command
            noErr: 'True' indicates that the errors doesn't have to be logged
            ErrorStrings: List of error strings to look for in the output. Found error will be considered as an error in the execution process
            Detached: Whether to execute seperately from the main process (Default: False)
            hidenStrings: List of strings tha has to be hiden in the output (used for hiding passwords)
        """
        if not isinstance(exe, list):
            args = shlex.split(exe)
        else:
            args = exe
            exe = " ".join(exe)
        _StartTime = datetime.datetime.now()
        if not Silent:
            command = exe
            for hideString in hidenStrings:
                command = command.replace(hideString, '*' * len(hideString))
            self.AddMessage(u'>Executing the Shell command> ' + command)
        ShellOutput = self._runProcess(args, noErr, Detached, Silent, hidenStrings)
        lines = ShellOutput
        self._outputLines(lines, False, noErr, ErrorStrings, Silent, hidenStrings = hidenStrings)
        _TD = datetime.datetime.now()- _StartTime
        if not Silent:
            self.AddMessage(u'>Done executing the Shell command. Execution time '  + str(_TD))

    def outputLogfile(self, file, encoding='utf8', noErr=False, ErrorStrings=['ERROR', 'FAILED', u'KĻŪDA', 'EXCEPTION', 'ORA-'], Silent=False, hidenStrings = []):
        """Procedure prints text file to screent - processing error keywords

        Args:
            self: The reserved object 'self'
            file: path to file to process
            noErr: True ir no error logging is necesery
            ErrorStrings: List or keywords with will be recognized as errors
            Silent: if True no Errors will be rised
            hidenStrings: List of strings tha has to be hiden in the output (used for hiding passwords)
        """
        with codecs.open(file, 'r', encoding) as fin:
            self._outputLines(fin.readlines(), True, noErr, ErrorStrings, Silent, hidenStrings = hidenStrings)

    def _outputLines(self, lines, doMessges, noErr=False, ErrorStrings=['ERROR', 'FAILED', u'KĻŪDA', 'EXCEPTION', 'ORA-'], Silent=False, hidenStrings = []):
        """Procedure for outputing set of lines to screen with error key word recognition. (for example for log file output processing)

        Args:
            self: The reserved object 'self'
            lines: Lines to process
            noErr: True ir no error logging is necesery
            ErrorStrings: List or keywords with will be recognized as errors
            Silent: if True no Errors will be rised
            hidenStrings: List of strings tha has to be hiden in the output (used for hiding passwords)
        """
        isError = False
        for line in lines:
            for hideString in hidenStrings:
                line = line.replace(hideString, '*' * len(hideString))
            line = self._tryCovertStringEncoding(line)
            if line != '':
                if doMessges == True and Silent==False:
                    self.AddMessage(line)
                if noErr == False:
                    for ErStr in ErrorStrings:
                        if line.upper().find(ErStr.upper()) > -1:
                            isError = True
        for line in lines:
            for hideString in hidenStrings:
                line = line.replace(hideString, '*' * len(hideString))
            line = self._tryCovertStringEncoding(line)
            if line != '':
                if isError == True:
                    self.AddWarning('>>>>' + line)

    def AutorizeNTWLocation(self, Adress, user, pwd):
        """Network directory authorization

        Args:
            self: The reserved object 'self'
            Adress: Network adress
            user: Username
            pwd: Password
        """
        self.runShell(self.CorrectStr(r"net use " + Adress + r" /delete /y"), True, [])
        self.runShell(self.CorrectStr(r'net use ' + Adress + r' "' + pwd + r'" /user:' + user), True, [])

    def GetSQL(self, Name):
        """Function gets the SQL file location from the installation directory

        Args:
            self: The reserved object 'self'
            Name: Filename without an extension

        Returns:
            SQL file full path
        """
        return self.ExecutePatch + '\\SQL\\' + Name + '.sql'

    def RunSQL(self, Name, user="#", pwd="#", SpoolFile='#', ErrorStrings=['ERROR', 'FAILED', u'KĻŪDA', 'EXCEPTION', 'ORA-'], params=[], DBType='Oracle', hidenStrings = [], DBName='#'):
        """Procedure for SQL file execution (only Oracle sqlplus supported)
        Typically used for execution, passing only SQL filename parameter

        Args:
            self: The reserved object 'self'
            Name: Filename without an extension
            u: Username
            p: Password
            SpoolFile: SQL output
            ErrorStrings: A list of keyword error strings that defines an error in the execution
            params: aditional parameters
            DBType: only Oracle is supported
            hidenStrings: List of strings tha has to be hiden in the output (used for hiding passwords)
            DBName: Oracle TNS name
        """
        if DBType.upper() == 'ORACLE':
            if pwd == "#":
                pwd = self.Pr.p
            if user == "#":
                user = self.Pr.u
            if DBName == "#":
                DBName = self.Pr.TNSName
            if SpoolFile == '#':
                SpoolFile = self.Pr.OutDir + '\\' + Name + self.MyNowFile() + 'SQL.outlog'
            hidenStrings.append(pwd)
            self.AchiveFiles(self.Pr.OutDir, self.Pr.OutDirArh, Name, False)
            self.runShell('sqlplus -L ' + user + '/' + pwd + '@' + DBName + ' @"' + self.GetSQL(Name) + '" "' + SpoolFile + '" ' + ' '.join(params), False, ErrorStrings, hidenStrings = hidenStrings)
        else:
            raise AttributeError('Provided DB Type is not supported!')

    def GetPS(self, Name, Path='#'):
        """Function gets the PowerShell file location from the installation directory

        Args:
            self: The reserved object 'self'
            Name: Filename without an extension
        """
        if Path == '#':
            self.ExecutePatch
        return Path + '\\PShell\\' + Name + '.ps1'

    def RunPS(self, Name, Args, Path='#'):
        """Procedure for the PowerShell file execution

        Args:
            self: The reserved object 'self'
            Name: Filename without an extension
            Args: Arguments
        """
        if Path == '#':
            self.ExecutePatch
        self.runShell('powershell -File "' + self.GetPS(Name, Path) + '" ' + Args)

    def run_with_limited_time(self, func, args, kwargs, time):
        """Runs a function with time limit

        Args:
            self: The reserved object 'self'
            func: The function to run
            args: The functions args, given as a tuple
            kwargs: The functions args, given as a tuple
            time: The time limit in seconds

        Returns:
            True if the function ended successfully. False if it was terminated.
        """
        p = Process(target=func, args=args, kwargs=kwargs)
        p.start()
        p.join(time)
        if p.is_alive():
            p.terminate()
            return False
        return True
