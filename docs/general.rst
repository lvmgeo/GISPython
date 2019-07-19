General information
===================

Installation
------------

Dependencies
************

- ArcGIS 10.x /recommended with newest patches and service packs/ (*GISPython* is currently running on production systems based on ArcGIS 10.2.1, ArcGIS 10.3.1 and has been tested on ArcGIS 10.6.1)
- Python 2.7 (included in ArcGIS installation) (arcpy and numpy modules included)
- Additional python modules:

  - `PyCrypto <http://www.voidspace.org.uk/python/modules.shtml#pycrypto>`_ (manual installation)
  - NTLM: ``pip install python-ntlm`` (included in package setup process)
  - Paramiko: ``pip install paramiko`` (included in package setup process)
  - patool: ``pip install patool`` (included in package setup process)
  - simpleJson: ``pip install simplejson`` (included in package setup process)

Package installation
********************
  
*GISPython* package is available on the `Python Package Index <https://pypi.python.org/pypi/GISPython>`_, so you can get it via pip::

	pip install GISPython
	
.. Note:: If pip isn’t installed, you can get it `here <https://packaging.python.org/installing/#install-pip-setuptools-and-wheel>`_!

Configuration & basic usage
---------------------------
	
Before using *GISPython* modules in custom geoprocessing scripts, you need to set up your scripting environment with `*SetupDefaultEnvironment* <https://github.com/lvmgeo/GISPython/blob/master/GISPython/SetupDefaultEnvironment.py>`_ module which also includes template for user scripts.
		
*SetupDefaultEnvironment* module also includes basic parameters (variable *paramsFileSource*) for parameter file (e.g. SysGISParams.py) which is important, because *GISPython* relies of several
parameters to be present to function successfully:

* OutDir - directory for storing script output log files ``OutDir = r'C:\GIS\Log\Outlog\'``
* OutDirArh - directory for storing script output log file archive (all non active files) ``OutDirArh = r'C:\GIS\Log\Outlog\Archive\'``
* ErrorLogDir - directory for storing script error log files ``ErrorLogDir = r'C:\GIS\Log\ErrorLog\'`` *(Important! This directory can be monitored for non empty files. If this directory has a file that is non empty - this indicates that a script has failed)*
* ErrorLogDirArh - directory for storing script error log files ``ErrorLogDirArh = r'C:\GIS\Log\ErrorLog\Archive'``
* TmpFolder - Temp folder ``TmpFolder = r'C:\GIS\tmp'``
* encodingPrimary - encoding of Windows shell ``encodingPrimary = 'cp775'``
* encodingSecondary - encoding of Windows unicode language used ``encodingSecondary = 'cp1257'``
* SetLogHistory - enable or disable Geoprocessing history logging ``SetLogHistory = False``

.. Note:: It is recommended to define additional script parameters in SysGISParams.py file, to keep the main code clean. Our approach is to define all the parameters that define current system environment be kept in this one file. In case of moving environment (e.g. test system and production system) this one file has the specific connections and can be easily modified without changing the scripts.

Recommendations
***************

Set up the variables at the beggining of the main function, to shorten the main code::

	Tool = self.Tool
	gp = Tool.gp
	callGP = Tool.callGP
	pj = os.path.join
	
Basic operations
****************

ArcPy function call::

	gpCaller = self.Tool.callGP
	slay = 'some_layer'
	callGP('AddField_management', slay, 'Day_TXT', 'TEXT', '#', '#', 10)
	callGP('AddField_management', slay, 'CAR', 'TEXT', '#', '#', 128)
	callGP('AddField_management', slay, 'WorkID', 'DOUBLE', 12, 0)
	callGP('AddField_management', slay, 'REC_DATE_FROM', 'DATE')
	
Tool message output::

	Tool = self.Tool
	self.Tool.AddMessage(u'This is a message')
	self.Tool.AddWarning(u'This is a warning')
	self.Tool.AddError(u'This is an error')
	
.. toctree::
   :maxdepth: 4