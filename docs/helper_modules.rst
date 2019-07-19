Helper modules
==============

Additional *GISPython* package modules

AGServerHelper
--------------

*Module contains procedures for typical operations with ArcGIS server. All procedures use token authorization. For procedures with NTLM authorization use AGServerHelperNTLM module.*

.. automodule:: AGServerHelper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********

Check if ArcGIS Server service is running::

	from GISPython import AGServerHelper

	Tool = self.Tool
	JsonParams = JsonParamsHelper.JsonParams(Tool, 'Config', 'ServiceCheck')
	AGS = AGServerHelper.AGSServerHelper(Pr.AGS_u, Pr.AGS_p, Pr.AGS_Servers[0], Pr.AGS_Port, self.Tool)
	configData = JsonParams.GetParams()
	dirs = configData[u'chechServiceList']
	for dir in dirs:
		services = dir["services"]
		for service in services:
			serviceName = service["serviceName"]
			type = service["type"]
			description = service["description"]
			try:
				running = AGS.IsServiceRunning(dir["folderName"], serviceName + "." + type)

				if running:
					Tool.AddMessage(u"\t{0}\\{1}.{2} ({3}) - OK".format(dir["folderName"], serviceName, type, description))
				else:
					txt = u"\t{0}\\{1}.{2} ({3}) - Stopped".format(dir["folderName"], serviceName, type, description)
					Tool.AddMessage(txt)
					errorTxt += "\n" + txt

			except Exception, e:
				tb = sys.exc_info()
				orgLine = "Line %i" % tb[2].tb_lineno
				orgTraceback = unicode(traceback.format_exc(), errors='ignore')

				txt = u"\t{0}\\{1}.{2} ({3}) - Error - Line:{4} Error: {5} ".format(dir["folderName"], serviceName, type, description, orgLine, orgTraceback)
				Tool.AddMessage(txt)
				errorTxt += "\n" + txt

AGServerHelperNTLM
------------------

*Module contains procedures for typical operations with ArcGIS server. All procedures use NTLM authorization. For token authorization use AGServerHelpaer module.*

.. automodule:: AGServerHelperNTLM
	:members:
	:undoc-members:
	:show-inheritance:

CachingHelper
-------------

*Module generates and carries out map scale caching in ArcGIS Server services.*

.. automodule:: CachingHelper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********

Daily server caching procedure::

	from GISPython import CachingHelper

	GCache = CachingHelper.CachingHelper(self.Tool, Pr.ConnAGSCache, self.Tool.gp.Extent(307950, 167920, 767480, 443890), Pr.ConnAuto + "\\SDEOWNER.CashLVBuffer")
	GCache.GenerateCache('Nog_Dalplans_cache',8,'30000;20000;15000;10000;5000;2000','CacheDinamic')
	GCache.GenerateCache('Nog_MezaudzuPlans_cache',8,'30000;20000;15000;10000;5000;2000','CacheDinamic')
	
FTPHleper
---------

*Module contains procedures for typical FTP server file operations.*

.. automodule:: FTPHleper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********

Deletes old and uploads new files to FTP server::

	from GISPython import FTPHleper

	tmpFolder = pj(Pr.TmpFolder, "mobileInfo")
	FTP = FTPHleper.FTPHleper(Pr.mobileFTPHost, Pr.mobileFTPuser, Pr.mobileFTPpwd, Pr.mobileFTPmobileinfoFolder)
	ftpfiles = FTP.list_files()

	# Delete old files
	for file in (f for f in ftpfiles if (f.file == 'file1.geojson' or f.file == 'file2.geojson')):
		Tool.AddMessage(u'Delete file ' + file.file + ' from ftp ...')
		FTP.delete_file(file.file)

	# Upload new files
	FTP.upload_file('file1.geojson', tmpFolder)
	Tool.AddMessage(u'\nfile ' + 'file2.geojson' + u' uploaded to ftp ...')
	FTP.upload_file('file2.geojson', tmpFolder)
	Tool.AddMessage(u'file ' + 'file2.geojson' + u' uploaded to ftp ...')
	
GDBHelper
---------

*Module for typical GDB (File Geodatabase) operations.*

.. automodule:: GDBHelper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********

Clear old data from a table or a feature class and append new data::

	from  GISPython import GDBHelper
	from GISPython import TimerHelper

	GDB = GDBHelper.GDBHelper(self.Tool.gp, self.Tool)
	Appender = GDBHelper.SimpleAppend(self.Tool, Pr.ConnAuto, Pr.VAADConn)
	t = TimerHelper.TimerHelper()
	layer = 'Dataset.Table'

	# Deletes old data
	self.Tool.AddMessage(u'\n>>>> Begin the old file deletion procedure {0}'.format(Tool.MyNow()))
	GDB.ClearData(Pr.Connection, layer)
	self.Tool.AddMessage(u'\n>>>> End the old file deletion procedure {0}'.format(t.GetTimeReset()))

	# Appends new data
	self.Tool.AddMessage(u'\n>>>> Begin data appending procedure {0}'.format(Tool.MyNow()))
	Appender.Append('SDEOWNER.MKViews\\SDEOWNER.TABLEVIEW1', layer)
	self.Tool.AddMessage(u'\n>>>> End data appending procedure {0}'.format(t.GetTimeReset()))

Validate the rows with the SQL clause::

	from GISPython import GDBHelper

	RHelper = GDBHelper.RowHelper(self.Tool.gp, self.Tool)

	# Validate rows
	rezultList = RHelper.ValidateRowsForSQLClause(fc, validator[u'Fields'], validator[u'Query'], validator[u'OutputPatern'])

	# Output message
	if len(rezultList)>0:
		self.Tool.AddMessage(u'         !!! {0} faulty records found ... '.format(len(rezultList)))
	
GDPSyncroniserHelper
--------------------

.. automodule:: GDPSyncroniserHelper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********

Synchronize data between two tables with internal parameter definition::

	from GISPython import GDPSyncroniserHelper

	ErrOutput = ''
	sync = GDPSyncroniserHelper.GDPSyncroniserHelper(gp, Tool)
	deff = GDPSyncroniserHelper.SyncDefinition()
	bridges = callGP('MakeFeatureLayer_management', pj(Pr.ConnAuto, 'SDEOWNER.Roads', 'SDEOWNER.Bridge'), '#', 'BRIDGESUBTYPE = 1')

	# Define input table parameters
	deff.inTable = bridges
	deff.inTableJoinField = 'OBJECTID' # join field
	deff.inTableFields = ('OBJECTID', 'BRIDGENUMBER', 'BRIDGENAME', 'LVM_DISTRICT_CODE','MI_SPECIALIST', 'MIREGION', 'SHAPE@XY') # fields

	# Define output table parameters
	deff.outTable = pj(Pr.ConnAuto, 'SDEOWNER.Roads', 'SDEOWNER.BridgeInspection')
	deff.outTableJoinField = 'BRIDGEOID' # join field
	deff.outTableFields = ('BRIDGEOID', 'BRIDGENUMBER', 'BRIDGENAME', 'LVM_DISTRICT_CODE','MI_SPECIALIST', 'MIREGION', 'SHAPE@XY') # fields
	deff.createNew = True
	deff.messageDefinition = u'Nr: {1} - {2}' # output mask 'inTableJoinField + inTableFields' defines sync order
	
	# End of synchronization
	output, outputErrors = sync.DoSync(deff, Pr.ConnAuto, True, True, True, True) 

	# Error message in case there are any error
	if not outputErrors == u"":
		ErrOutput += u'Found errors in synchronization process:\n' + outputErrors + '\n\n';

GDPSyncroniserHelper2
--------------------

.. automodule:: GDPSyncroniserHelper2
	:members:
	:undoc-members:
	:show-inheritance:

	
JsonParamsHelper
----------------

.. automodule:: JsonParamsHelper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********

Update attributes from JSON file::

	from GISPython import JsonParamsHelper

	# User defined data update function
	def UpdateData(self, key, configData, origKey):
		 """Executes attribute selection from configuration file and pass the parameters to the attribute calculation tool

		 Args:
			self: The reserved object 'self'
			key: Dictionary key, which corresponds to the 'rightsType' argument
			configData: Retrieved data from the configuration file
			origKey: Primary rights type
		"""

	def mainModule(self, rightsType = '#'):
		#Define variables
		rightsType = self.rightsType

		JsonParams = JsonParamsHelper.JsonParams(self.Tool, 'ConfigFolder', 'ConfigFile')
		configData = JsonParams.GetParams()

		# Call UpdateData function (user defined) with according rights
		if (rightsType.upper() == "ALL" or rightsType.upper() == "SOMETYPE"):
			for key in configData.keys():
				self.UpdateData(key, configData, rightsType)
		else:
			self.UpdateData(rightsType, configData, rightsType)


	
MailHelper
----------

*Module for e-mail operations. Module contains functions for typical SMTP operations, and parameter processing from user parameter file.*

.. automodule:: MailHelper
	:members:
	:undoc-members:
	:show-inheritance:
	
Examples
********
Send e-mail using parameters from parameter file::

	from  GISPython import MailHelper

	MailHelper.GISPythonMailHelper(self.Pr, ['***@mail.com'], 'Subject', 'e-mail content')

This script depends on following parameters which needs to be configured in *SysGISParams.py* file:

* Mailserver - mail server name ``Mailserver = 'mail.server.com'``
* MailserverPort - mail server port number ``MailserverPort = 587``
* MailserverUseTLS - use TLS in mail server? ``MailserverUseTLS = True``
* MailserverUseSSL - use SSL in mail server? ``MailserverUseSSL = False``
* MailserverUser - user name ``MailserverUser = 'UserName``
* MailserverPWD - user password ``MailserverPWD = r'userPassword'``
* MailFromAdress - e-mail adress from which to send the e-mail ``MailFromAdress = 'userAdress@mail.com'``

Send e-mail::

	from  GISPython import MailHelper

	mailSender = MailHelper.MailHelper('mail@from.com', ['***@mail.com'], 'Subject', u'e-mail content') # Set up the e-mail for sending
	mailSender.SendMessage('smtp.server.com', 587, 'username', 'password', useTLS=True) # Send e-mail
	
MyError
-------

*Module contains class for storing an error object.*

.. automodule:: MyError
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********
Raise error in the tool output::

	from geopythoncore import MyError

	l = 12
	linecount = 10
	if linecount != l-2:
		raise MyError.MyError(u'Error in line count') # Add the error in the tool output

PublisherHelper
---------------

*Module for deployment operations.*

.. automodule:: PublisherHealper
	:members:
	:undoc-members:
	:show-inheritance:

RarHelper
---------

.. automodule:: RarHelper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********
Extract the Rar file::

	from GISPython import RarHelper

	# File extraction procedure
	RH = RarHelper.RarHelper()
	rarFile = 'c:\\tmp\fileName.rar' # Rar file full path
	workDir = 'c:\\tmp\someDirectory' # Directory in which to extract the Zip file
	RH.ExtractRarFile(rarFile, workDir) # Extraction procedure

	
SFTPHelper
----------

.. automodule:: SFTPHelper
	:members:
	:undoc-members:
	:show-inheritance:

Examples
********

Function which compresses files and sends to SFTP server::

	from GISPython import SFTPHelper 
	from GISPython import ZipHelper

	tmpFolder  = os.path.join(Pr.TmpFolder, 'DataFolder')
	WorkDBName = 'DBName'
	WorkDB = callGP('CreateFileGDB_management', tmpFolder, WorkDBName)
	zipFileName = os.path.join(tmpFolder, WorkDBName + self.Tool.MyNowFile() + '.zip')
	ZIP = ZipHelper.ZipHelper()
	ZIP.CompressDir(WorkDB, zipFileName, ['lock']) # Compress directory contents

	# Call parameters from the external parameter file
	SFTP = SFTPHelper.SFTPHelper(Pr.SFTPUser, Pr.SFTPPwd, Pr.SFTPHost, Pr.SFTPPort)
	SFTP.upload(zipFileName, os.path.basename(zipFileName)) # Upload file to SFTP
	
SimpleFileOps
-------------

*File and filesystem operations module. Module contains functions for typical file and filesystem operations, and locking control and processing.
This module uses windows PowerShell to address file locking situations. For module with the same functionality without PowerShell script usage use *SimpleFileOpsSafe* module.*

.. automodule:: SimpleFileOps
	:members:
	:undoc-members:
	:show-inheritance:
	
Examples
********
Check for the directory, and clear its contents::

	from  GISPython import SimpleFileOps

	FO = SimpleFileOps.SimpleFileOps(self.Tool)
	workDir = pj(Pr.TmpFolder, 'WorkingDirectory') # Set the working directory
	FO.CheckCreateDir(workDir) # Check if directory exists, if not, create the directory
	FO.ClearDir(workDir) # Clear directory contents
	
Find the newest file in the directory and create a backup::

	from  GISPython import SimpleFileOps

	FO = SimpleFileOps.SimpleFileOps(self.Tool)
	workDir = pj(Pr.TmpFolder, 'WorkingDirectory') # Set the working directory
	backupDir = pj(Pr.TmpFolder, 'BackupDirectory') # Set the working directory
	newFile = FO.FindNewestFile(workDir, '*') # Find newest file with any extension
	FO.BackupOneFile(newFile, backupDir)
	
SimpleFileOpsSafe
-----------------

*File and filesystem operations module. Module contains SimpleFileOpsSafe class, which contains functions for typical file and filesystem operations. Class inherits SimpleFileOps functionality, but does not relay on Windows Powershell scripts to address locked files.*

.. automodule:: SimpleFileOpsSafe
	:members:
	:undoc-members:
	:show-inheritance:
	
TimerHelper
-----------

*Timing module. Module contains functions for countdown procedures in a code block.*

.. automodule:: TimerHelper
	:members:
	:undoc-members:
	:show-inheritance:
	
Examples
********
Add a message to the tool output::

	from  GISPython import TimerHelper

	with TimerHelper.TimedSubprocess(self.Tool, u'some process'):
			# Your code
			self.Tool.AddMessage(u'some action')
		
Output::

	------------------------
	>>>> Begin some process - yyyy-mm-dd hh:mm:ss
	------------------------
	some action
	
	------------------------
	>>>> End some process - h:mm:ss.ssssss
	------------------------

xmlParamsHelper
----------------

*Module for XML parameter file procedures*.

.. automodule:: xmlParamsHealper
	:members:
	:undoc-members:
	:show-inheritance:

ZipHelper
---------

*Zip file operations module. Module contains functions for common Zip file operations.*

.. automodule:: ZipHelper
	:members:
	:undoc-members:
	:show-inheritance:
   
Examples
********
Archiving procedure::

	from  GISPython import ZipHelper

	ZH = ZipHelper.ZipHelper()
	workDir = 'c:\\tmp\someDirectory' # Directory to archive
	zipFile = 'c:\\tmp\fileName' + self.Tool.MyNowFileSafe() + '.zip' # New zip file with formatted date (simple example)
	zipFile = 'c:\\tmp\fileName{0}.zip'.format(self.Tool.MyNowFileSafe()) # New zip file with formatted date (good example)
	ZH.CompressDir(workDir, zipFile)

Extraction procedure::

	from  GISPython import ZipHelper

	ZH = ZipHelper.ZipHelper()
	workDir = 'c:\\tmp\someDirectory' # Directory in which to extract the Zip file
	zipFile = 'c:\\tmp\fileName{0}.zip'.format(self.Tool.MyNowFileSafe()) # Zip file with formatted date
	ZH.ExtractZipFile(zipFile, workDir)

.. toctree::
   :maxdepth: 4