# ![img](http://www.lvmgeo.lv/images/lvmgeo/backgrouds/icons/python_small.svg) LVM GEO Python Core (_GISPython_)

LVM GEO Python Core (_GISPython_) is an open source automation and scripting core developed by the LVM GEO team. Based on this core any developer can build simple and structured Python programming scripts with a rich functionality. The programming core allows management of all system's maintenance processes within a unified environment.

There are many automated maintenance operations necessary for every large geospatial information system (GIS). These operations are required for database and server maintenance, data validations and calculations, map preparing and caching, or data exchange with other systems. Within ERSI platform maintenance scripting is done by Python programming language and ArcPy library. The LVM GEO team has worked with ArcPy library for many years and has developed the LVM GEO Python Core complementing and enriching the Platform maintenance possibilities of the ESRI library that are not provided in the ArcPy standard:
* monitoring of automated scripts (for example Zabbix)
* script audit storage
* generation of automated e-mails (script progress status reports as well as automated data validation warning e-mails, etc.)
* data transfer using FTP and SFTP, data compressing and uncompressing
* SQL, PowerShell, Windows Shell file initiation and progress monitoring within an unified environment with ArcPy geoprocessing tools

The Core also includes tools that simplify usage of ArcPy and Python functions, significantly easing the development process:
* scripting of ArcGIS server administration
* scripting of file operations
* scripting of service caching
* unified script initiation from ArcGIS environment, Python Shell and from other tools
* etc.

The LVM GEO Python Core is already being used by several companies in Latvia, including JSC Latvia's State Forests for more than 200 automated processes every day. LVM GEO offers courses about LVM GEO Python to support development of an automation platform for companies and organizations.

### _GISPython_ package contains following modules:
* [**Main modules**](http://gispython.readthedocs.io/en/latest/main_modules.html):
    * [GISPythonModule](http://gispython.readthedocs.io/en/latest/main_modules.html#gispythonmodule)
    * [GISPythonTool](http://gispython.readthedocs.io/en/latest/main_modules.html#gispythontool)
    * [SysGISTools](http://gispython.readthedocs.io/en/latest/main_modules.html#sysgistools)
    * [SysTools_unittest]()
* [**Helper modules**](http://gispython.readthedocs.io/en/latest/helper_modules.html):
    * [AGServerHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#agserverhelper)
    * [AGServerHelperNTLM](http://gispython.readthedocs.io/en/latest/helper_modules.html#agserverhelperntlm)
    * [CachingHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#cachinghelper)
    * [FTPHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#ftphleper)
    * [GDBHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#gdbhelper)
    * [GDPSynchroniserHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#module-GISPython.GDPSyncroniserHelper)
    * [JsonParamsHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#jsonparamshelper)
    * [MailHelper](https://github.com/lvmgeo/GISPython#mailhelper)
    * [MyError](http://gispython.readthedocs.io/en/latest/helper_modules.html#myerror)
    * [RarHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#rarhelper)
    * [SFTPHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#sftphelper)
    * [SimpleFileOps](http://gispython.readthedocs.io/en/latest/helper_modules.html#simplefileops)
    * [SimpleFileOpsSafe](http://gispython.readthedocs.io/en/latest/helper_modules.html#simplefileopssafe)
    * [TimerHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#timerhelper)
    * [ZipHelper](http://gispython.readthedocs.io/en/latest/helper_modules.html#ziphelper)

## Dependencies

* ArcGIS 10.x /recommended with newest patches and service packs/ (**_GISPython_** is currently running on production systems based on ArcGIS 10.2.1, ArcGIS 10.3.1 and has been tested on ArcGIS 10.4)
* Python 2.7 (included in ArcGIS installation) (arcpy and numpy modules included)
* Additional python modules:
    * [PyCrypto](http://www.voidspace.org.uk/python/modules.shtml#pycrypto) (manual installation)
    * NTLM: `pip install python-ntlm` (included in package setup process)
    * paramiko: `pip install paramiko` (included in package setup process)
    * patool: `pip install patool` (included in package setup process)
    * simpleJson: `pip install simplejson` (included in package setup process)
    
>If pip isn’t installed, you can get it [**here**](https://packaging.python.org/installing/#install-pip-setuptools-and-wheel)!

## Installation

**_GISPython_** is available on the [Python Package Index](https://pypi.python.org/pypi/GISPython), so you can get it via pip: `pip install GISPython`.
Before installing it is recomended to upgrade pip to latest version using `pip install --upgrade pip`.
To upgrade **_GISPython_** use `pip install gispython --upgrade`.

## Configuration & basic usage

Before using **_GISPython_** modules in custom geoprocessing scripts, you need to set up your scripting environment.
Here is an example of **_GISPython_** script:
```python
# -*- coding: utf-8 -*-
"""
    Tool description
"""
import SysGISParams as Pr # Import custom parameter file
import sys, os # Import built in Python modules for basic operations
from  GISPython import GISPythonModule # Import scripting framework from  GISPython package
# you can import additional  GISPython modules, based on the tool's needs

#Base class of the module
class MainModule(GISPythonModule.GISPythonModule): # Inherits GISPythonModule class
	"""
		Base module of the tool
	"""
	def __init__(self):
        """
            Class initialization procedure
        """
		GISPythonModule.GISPythonModule.__init__(self, 'ToolName', Pr, __file__)
		
	def mainModule(self, args):
		"""
			Base procedure of the tool
		"""
		# Your code
		
# Module execution
if __name__ == "__main__":
	"""Module execution"""
	Module = MainModule()
	Module.DoJob()
```
Parameter file or object (e.g. SysGISParams.py) is important, because **_GISPython_** relies of several parameters to be present to function successfully:
* OutDir - directory for storing script output log files `OutDir = r'C:\GIS\Log\Outlog\' `
* OutDirArh - directory for storing script output log file archive (all non active files) `OutDirArh = r'C:\GIS\Log\Outlog\Archive\' `
* ErrorLogDir - directory for storing script error log files `ErrorLogDir = r'C:\GIS\Log\ErrorLog\' `(*Important! This directory can be monitored for non empty files. If this directory has a file that is non empty - this indicates that a script has failed*)
* ErrorLogDirArh - directory for storing script error log files `ErrorLogDirArh = r'C:\GIS\Log\ErrorLog\Archive' `
* TmpFolder - Temp folder `TmpFolder = r'C:\GIS\tmp'`
* encodingPrimary - encoding of Windows shell `encodingPrimary = 'cp775' `
* encodingSecondary - encoding of Windows unicode language used `encodingSecondary = 'cp1257' `

>It is recommended to define additional script parameters in SysGISParams.py file, to keep the main code clean. Our approach is to define all the parameters that define current system environment be kept in this one file. In case of moving environment (e.g. test system and production system) this one file has the specific connections and can be easily modified without changing the scripts.

### Recommendations
Set up the variables at the beggining of the main function, to shorten the main code:
```python
Tool = self.Tool
gp = Tool.gp
callGP = Tool.callGP
pj = os.path.join
```

### Basic operations:
ArcPy function call:
```python
gpCaller = self.Tool.callGP
slay = 'some_layer'
callGP('AddField_management', slay, 'Day_TXT', 'TEXT', '#', '#', 10)
callGP('AddField_management', slay, 'CAR', 'TEXT', '#', '#', 128)
callGP('AddField_management', slay, 'WorkID', 'DOUBLE', 12, 0)
callGP('AddField_management', slay, 'REC_DATE_FROM', 'DATE')
```
Tool message output:
```python
Tool = self.Tool
self.Tool.AddMessage(u'This is a message')
self.Tool.AddWarning(u'This is a warning')
self.Tool.AddError(u'This is an error')
```

## Documentation

Documentation includes information about all GISPython modules & examples of use. Documentation can be found on: http://gispython.readthedocs.io.

## Examples

### Main modules

#### _GISPythonModule_
Main module, which contains frame for all  GISPython package modules. Module allows the code unification, and ensures the code execution from both the ArcGIS Desktop Python console and the Command Prompt.

_Example:_
###### Executes the tool if it's to be executed within an another Python tool
```Python
from  GISPython import TimerHelper
import OnlineCompress
with TimerHelper.TimedSubprocess(Tool, u'Compress DB'): # Adds a message to the tool output
    with TimerHelper.TimedSubprocess(Tool, u'disconnect users from DB', 2): # Adds a message to the tool output
        self.Tool.RunSQL('KillUsers', Pr.u_sde, Pr.p_sde) # Runs custom SQL script
    OnlineCompress.MainModule(None, False).runInsideJob(Tool) # Runs SDE Compression procedure from OnlineCompress module (custom geoprocessing module)
```

#### _GISPythonTool_
Module defines abstract classes for the ESRI Toolbox tool definition and contains functions which helps to create an ArcGIS Toolbox, validates the tool's parameter values and controls a behavior of the tool's dialog.

_Example:_
###### Define parameters in ESRI Python toolbox
```Python
from  GISPython import GISPythonTool
class ToolManageArcGISServer(GISPythonTool.GISPythonTool): # Custom Python tool
    def __init__(self): # Class initialization procedure
        """Define the tool (tool name is the class name)"""
        self.label = u"Tool for administering the ArcGIS server"
        self.description = u"Tool for administering the ArcGIS server"
        self.category = 'Administrator tools'
        
    def updateParameters(self, parameters): # Call this method from GISPythonTool in case the parameters are changed, and set up the parameters
        if parameters[3].value == True:
            parameters[2].enabled = True
        else:
            parameters[2].enabled = False
        return parameters
        
    def updateMessages(self, parameters): # Call this method from GISPythonTool after an inner validation. Method carries out an additional validations
        if parameters[2].value is None and parameters[3].value == True:
            parameters[2].setErrorMessage("To change the MXD file connection, you need to indicate connection path, ")
        else:
            parameters[2].clearMessage()
        return parameters
```

#### _SysGISTools_
Base module which contains GISPython scripting framework, logging, error processing and automation mechanisms for different operations, and module and interface base classes.

_Examples:_
###### Run a script from Shell with parameters
```Python
Tool = self.Tool
# Executes your custom process script (mainly maintenance scripts) within runShell function,
# which implements _runProcess function (message output in terminal window).
# Function executes script seperately from main process (Detached=True) and indicates, 
# that the errors doesn't have to be logged (noErr=True).
Tool.runShell('SomeProcess.py', Detached = True, noErr = True)
time.sleep(10) # after 10 seconds launch another runShell process
```

###### Executes a custom SQL script file (only Oracle sqlplus supported)
```Python
from  GISPython import TimerHelper
Tool = self.Tool
# Executes process from SQL file
with TimerHelper.TimedSubprocess(self.Tool, u'datu atlasi no nogabaliem'): # Adds a message to the tool output
    Tool.RunSQL('LoadSomeDataFromTable') # Runs SQL file within RunSQL function, which implements GetSQL function (gets the SQL file location)
```

###### Duplicates path seperator symbol '\' for external execution compatibility
```Python
from  GISPython import SimpleFileOps
from  GISPython import TimerHelper
Tool = self.Tool
#...
with TimerHelper.TimedSubprocess(Tool, u'prepare environment'): # Adds a message to the tool output
    DirHelper = SimpleFileOps.SimpleFileOps(Tool) # Set variable for SimpleFileOps module functions
    tmpFolder = os.path.join(Pr.TmpFolder, "Soil") # Set tmp folder path
    #...
    Tool.AddMessage(u'\n        ...delete previous tmp data') # Add tool output message
    DirHelper.CheckCreateDir(Tool.CorrectStr(tmpFolder)) # Check/create tmp directory (with modified path seperators)
    DirHelper.ClearDir(Tool.CorrectStr(tmpFolder)) # Clear tmp directory (with modified path seperators)
```

### Helper modules

#### _MailHelper_
Module for e-mail operations. Module contains functions for typical SMTP operations, and parameter processing from user parameter file.

_Examples:_
###### Send e-mail using parameters from parameter file
```python
from  GISPython import MailHelper
MailHelper.GISPythonMailHelper(self.Pr, ['***@mail.com'], 'Subject', 'e-mail content')
```
This script depends on following parameters which needs to be configured in _SysGISParams.py_ file:
* Mailserver - mail server name `Mailserver = 'mail.server.com'`
* MailserverPort - mail server port number `MailserverPort = 587`
* MailserverUseTLS - use TLS in mail server? `MailserverUseTLS = True`
* MailserverUseSSL - use SSL in mail server? `MailserverUseSSL = False`
* MailserverUser - user name `MailserverUser = 'UserName`
* MailserverPWD - user password `MailserverPWD = r'userPassword'`
* MailFromAdress - e-mail adress from which to send the e-mail `MailFromAdress = 'userAdress@mail.com'`

###### Send e-mail
```python
from  GISPython import MailHelper
mailSender = MailHelper.MailHelper('mail@from.com', ['***@mail.com'], 'Subject', u'e-mail content') # Set up the e-mail for sending
mailSender.SendMessage('smtp.server.com', 587, 'username', 'password', useTLS=True) # Send e-mail
```

#### _SimpleFileOps_
File and filesystem operations module. Module contains functions for typical file and filesystem operations, and locking control and processing.
This module uses windows PowerShell to address file locking situations. For module with the same functionality without PowerShell script usage use _SimpleFileOpsSafe_.

_Examples:_
###### Check for the directory, and clear its contents
```python
from  GISPython import SimpleFileOps
FO = SimpleFileOps.SimpleFileOps(self.Tool)
workDir = pj(Pr.TmpFolder, 'WorkingDirectory') # Set the working directory
FO.CheckCreateDir(workDir) # Check if directory exists, if not, create the directory
FO.ClearDir(workDir) # Clear directory contents
```

###### Find the newest file in the directory and create a backup
```python
from  GISPython import SimpleFileOps
FO = SimpleFileOps.SimpleFileOps(self.Tool)
workDir = pj(Pr.TmpFolder, 'WorkingDirectory') # Set the working directory
backupDir = pj(Pr.TmpFolder, 'BackupDirectory') # Set the working directory
newFile = FO.FindNewestFile(workDir, '*') # Find newest file with any extension
FO.BackupOneFile(newFile, backupDir)
```

#### _TimerHelper_
Timing module. Module contains functions for countdown procedures in a code block.

_Example:_
###### Add a message to the tool output
```python
from  GISPython import TimerHelper
with TimerHelper.TimedSubprocess(self.Tool, u'some process'):
    self.Tool.AddMessage(u'some action')
```
![img_time.png](https://github.com/lvmgeo/GISPython/blob/master/img/img_time.png)

#### _ZipHelper_
Zip file operations module. Module contains functions for common Zip file operations.

_Examples:_
###### Archiving procedure
```python
from  GISPython import ZipHelper
ZH = ZipHelper.ZipHelper()
workDir = 'c:\\tmp\someDirectory' # Directory to archive
zipFile = 'c:\\tmp\fileName' + self.Tool.MyNowFileSafe() + '.zip' # New zip file with formatted date (simple example)
zipFile = 'c:\\tmp\fileName{0}.zip'.format(self.Tool.MyNowFileSafe()) # New zip file with formatted date (good example)
ZH.CompressDir(workDir, zipFile)
```

###### Extraction procedure
```python
from  GISPython import ZipHelper
ZH = ZipHelper.ZipHelper()
workDir = 'c:\\tmp\someDirectory' # Directory in which to extract the Zip file
zipFile = 'c:\\tmp\fileName{0}.zip'.format(self.Tool.MyNowFileSafe()) # Zip file with formatted date
ZH.ExtractZipFile(zipFile, workDir)
```

## Contributing
We encourage developers to use LVM GEO Python Core code and also contribute to the project. LVM GEO team is open for cooperation in developing new solutions, provides LVM GEO Python courses and offers to implement a fully functional automation platform for companies and organizations for their business needs.

## Licensing

[GPL-3.0+](https://choosealicense.com/licenses/gpl-3.0/)

## Copyright

[![LVMGEO](https://github.com/lvmgeo/GISPython/blob/master/img/LVM_GEO-logo-PMS30.PNG)](http://www.lvmgeo.lv/en "Copyright (c) 2017 LVM GEO")
