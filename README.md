# geopythoncore
![python_large.png](https://bitbucket.org/repo/eky5EEp/images/957292278-python_large.png)

---------
Droši vien jāliek arī kaut kas no Katrīnas iztulkotā teksta.

geopythoncore package contains following modules:

* [Main modules](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-main-modules):
    * [GISPythonModule](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-gispythonmodule)
    * [GISPythonTool](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-gispythontool)
    * [SysGISTools](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-sysgistools)
    * [SysGISToolsSysParams](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-sysgistoolssysparams)
    * SysTools_unittest (Coming soon)
* [Helper modules](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-helper-modules):
    * AGServerHelper (Coming soon)
    * CachingHelper (Coming soon)
    * FTPHelper (Coming soon)
    * GDBHelper (Coming soon)
    * GDPSynchroniserHelper (Coming soon)
    * JsonParamsHelper (Coming soon)
    * [MailHelper](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-mailhelper)
    * [MyError](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-myerror)
    * RarHelper (Coming soon)
    * SFTPHelper (Coming soon)
    * [SimpleFileOps](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-simplefileops)
    * [SimpleFileOpsSafe](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-simplefileopssafe)
    * [TimerHelper](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-timerhelper)
    * [ZipHelper](https://bitbucket.org/arturspd/geopythontest/overview#markdown-header-ziphelper)

---------
## Dependencies
* ArcGIS 10.3.1 (recommended with newest patches and service packs)
* Python 2.7 (usually included in ArcGIS installation) (arcpy module included)
* Additional python modules:
    * [PyCrypto](http://www.voidspace.org.uk/python/modules.shtml#pycrypto)
    * Paramiko: `pip install paramiko` (included in package setup process)
    * simpleJson: `pip install simplejson` (included in package setup process)
    
>If pip isn’t installed, you can get it [**here**](https://packaging.python.org/installing/#install-pip-setuptools-and-wheel)!

---------

## Installation

_geopythoncore_ is available on the Python Package Index (te nāks iekšā links), so you can get it via pip: `pip install geopythoncore`

---------
## Configuration & basic usage

Before using _geopythoncore_ modules in custom geoprocessing scripts, you need to set up your scripting environment:
```python
# -*- coding: utf-8 -*-
"""
    Tool description
"""
import SysGISParams as Pr # Import custom parameter file
import sys, os # Import built in Python modules for basic operations
from geopythoncore import GISPythonModule # Import scripting framework from geopythoncore package
# you can import additional geopythoncore modules, based on the tool's needs

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
>It is recommended to define additional script parameters in SysGISParams.py file (included in package), to keep the main code clean.

### Recommendations
Set up the variables at the beggining of the main function, to shorten the main code

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

---------
## Modules & examples of use

### Main modules

#### _GISPythonModule_
Main module, which contains frame for all geopythoncore package modules. Module allows the code unification, and ensures the code execution from both the ArcGIS Desktop Python console and the Command Prompt.

#### _GISPythonTool_
Module defines abstract classes for the ESRI Toolbox tool definition and contains functions which helps to create an ArcGIS Toolbox, validates the tool's parameter values and controls a behavior of the tool's dialog.

#### _SysGISTools_
Base module which contains GISPython scripting framework, logging, error processing and automation mechanisms for different operations, and module and interface base classes.
 
#### _SysGISToolsSysParams_
Module contains information about package version.

### Helper modules

#### _MailHelper_
Module for e-mail operations. Module contains functions for typical SMTP operations, and parameter processing from user parameter file.

_Examples:_

##### Send e-mail using parameters from parameter file
```python
from geopythoncore import MailHelper
MailHelper.GISPythonMailHelper(self.Pr, ['***@mail.com'], 'Subject', 'e-mail content')
```

##### Send e-mail
```python
from geopythoncore import MailHelper
mailSender = MailHelper.MailHelper('mail@from.com', ['***@mail.com'], 'Subject', u'e-mail content') # Set up the e-mail for sending
mailSender.SendMessage('smtp.server.com', 587, 'username', 'password', useTLS=True) # Send e-mail
```

#### _MyError_
Error module, which contains class for storing an error object.

_Example:_

##### Raise error in the tool output
```python
from geopythoncore import MyError
l = 12
linecount = 10
if linecount != l-2:
    raise MyError.MyError(u'Error in line count') # Add the error in the tool output
```

#### _SimpleFileOps_
File and filesystem operations module. Module contains functions for typical file and filesystem operations, and locking control and processing.

_Examples:_

##### Check for the directory, and clear its contents
```python
from geopythoncore import SimpleFileOps
FO = SimpleFileOps.SimpleFileOps(self.Tool)
workDir = pj(Pr.TmpFolder, 'WorkingDirectory') # Set the working directory
FO.CheckCreateDir(workDir) # Check if directory exists, if not, create the directory
FO.ClearDir(workDir) # Clear directory contents
```

##### Find the newest file in the directory and create a backup
```python
from geopythoncore import SimpleFileOps
FO = SimpleFileOps.SimpleFileOps(self.Tool)
workDir = pj(Pr.TmpFolder, 'WorkingDirectory') # Set the working directory
backupDir = pj(Pr.TmpFolder, 'BackupDirectory') # Set the working directory
newFile = FO.FindNewestFile(workDir, '*') # Find newest file with any extension
FO.BackupOneFile(newFile, backupDir)
```

#### _SimpleFileOpsSafe_
File and filesystem operations module. Module contains SimpleFileOpsSafe class, which contains functions for typical file and filesystem operations. Class inherits SimpleFileOps class from SimpleFileOps module. 

#### _TimerHelper_
Timing module. Module contains functions for countdown procedures in a code block.

_Example:_

##### Add a message to the tool output
```python
from geopythoncore import TimerHelper
with TimerHelper.TimedSubprocess(self.Tool, u'some process'):
    self.Tool.AddMessage(u'some action')
```
![img_time.png](https://bitbucket.org/repo/p44x65A/images/420010640-img_time.png)


#### _ZipHelper_
Zip file operations module. Module contains functions for common Zip file operations.

_Examples:_

##### Archiving procedure
```python
from geopythoncore import ZipHelper
ZH = ZipHelper.ZipHelper()
workDir = 'c:\\tmp\someDirectory' # Directory to archive
zipFile = 'c:\\tmp\fileName' + self.Tool.MyNowFileSafe() + '.zip' # New zip file with formatted date (simple example)
zipFile = 'c:\\tmp\fileName{0}.zip'.format(self.Tool.MyNowFileSafe()) # New zip file with formatted date (good example)
ZH.CompressDir(workDir, zipFile)
```

##### Extraction procedure
```python
from geopythoncore import ZipHelper
ZH = ZipHelper.ZipHelper()
workDir = 'c:\\tmp\someDirectory' # Directory in which to extract the Zip file
zipFile = 'c:\\tmp\fileName{0}.zip'.format(self.Tool.MyNowFileSafe()) # Zip file with formatted date
ZH.ExtractZipFile(zipFile, workDir)
```

---------
## Contributing
Teksts ar aicinājumu līdzdarboties projektā

---------
## Licensing
Licence (par šito jāpadomā)
[MIT, Apache vai GPL](https://choosealicense.com/)

---------

![BSRLogo.PNG](https://bitbucket.org/repo/eky5EEp/images/2304105760-BSRLogo.PNG)