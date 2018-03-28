=========
Changelog
=========

v1.36.2 (2018.03.04)
--------------------

* Added additional capabilities for GDBHelper

v1.36.1 (2018.02.25)
--------------------

* Added additional capabilities in shell command running
* Bug fixes in SimpleFileOps file locking functionality
* Added possibility to store time in date time parametrs in Json parameter file

v1.35.2 (2018.01.13)
--------------------

* Additional functionality added to SysGISTools module:
	- As there is many performance problems with *arcpy* geoprocessing script history logging, GISPython sets by default for *arcpy* not to log GP history. You can change this behavior by setting ``SetLogHistory = True`` in parameters file
	- GISPython Shell command launcher and SQL command launcher has added capabilities to hide passwords that they do not apear in output (logfiles and on screen)

v1.35.1 (2017.11.09)
--------------------

* Added GDPSyncroniserHelper2 module
* Changes and bug fixes in:
	- AGServerHelperNTLM
	- SimpleFileOps
	- SysGISTools
	- GISPythonModule
	- GDPSyncroniserHelper
* Added functionality in GDBHelper

v1.34.3 (2017.07.10)
--------------------

* Aditional functionality helping of reprinting MyError objects

v1.34.2 (2017.06.19)
--------------------

* Bug fixes in unicode output management
* Added functionality in SimpleFileOps and SimpleFileOpsSafe

v1.34.1 (2017.06.09)
--------------------

* Released documentation on Read The Docs
* Renamed AGSServerHelpaer module and class to AGSServerHelper
* Added AGSServerHelperNTLM module
* Added additional package dependencies (python-ntlm, patool)
* More module examples
* Modified README.md

v1.33.1 (2017.06.05)
--------------------

* Initial release

.. toctree::
   :maxdepth: 4