=========
Changelog
=========
v1.58.1 and (fix) v1.58.2 (2022.08.29)
--------------------
* AGServerHelperNTLM - added function cleanServicePermisions to remove rights from services

v1.57.1 (2022.07.15)
--------------------
* SFTPHelper - added list_files ability
* SFTPHelper - added delete_file ability

v1.56.1 (2022.04.21)
--------------------
* MailHelper - added ability to attach files to GISPythonMailHelper
* GISPythonModule - added ability to get log files in error and status e-mails of platform

v1.55.6 (2022.03.19)
--------------------
* MXDHelper - fix of bug, in error reporting

v1.55.5 (2022.03.17)
--------------------
* GDPSyncroniserHelper2 - fix of bug, when Shape fields wuld not sync if changes are minor

v1.55.4 (2022.03.16)
--------------------
* AGServerHelperNTLM - minor bug fixes

v1.55.3 (2022.02.21)
--------------------
* GDBHelper - CalculateXY bug fixes

v1.55.2 (2022.01.23)
--------------------
* GDBHelper - GetRelations added ability to add only child tables
* minor documentation fixes
* minor bug fixes

v1.55.1 (2022.01.22)
--------------------
* combined functionality of AGServerHelperNTLM and AGServerHelperToken - now AGServerHelperNTLM supports token authentication
* AGServerHelperNTLM - added function for publishing MXD files

v1.54.3 (2021.08.25)
--------------------
* fix errors in GISPythonToolBase.py

v1.54.2 (2021.08.10)
--------------------
* fix errors in AGServerHelperToken and AGServerHelperNTLM

v1.54.1 (2021.07.13)
--------------------
* Added new Module AGServerHelperToken - with replaces AGSServerHelper and supports all the methods avalable in AGServerHelperNTLM. Module is used for AGS management with tocken autentification

v1.53.2 (2021.03.26)
--------------------
* fix deploy error in PublisherHealper

v1.53.1 (2021.03.11)
--------------------
* Optimization of AGServerHelperNTLM

v1.52.1 (2021.02.12)
--------------------
* added xmlParamsHelper ability to provide namespaces if searching by XPath

v1.51.1 (2021.02.11)
--------------------
* fix errors in PublisherHealper for publishing whole folders with recursive option

v1.50.2 (2020.11.25)
--------------------
* fix errors in PublisherHealper

v1.50.1 (2020.10.08)
--------------------
* changes to GDBHelper - added ability to get all field names for table

v1.49.0 (2020.10.08)
--------------------
* changes to PublisherHealper - added ability to backup only changed files

v1.48.0 (2020.09.17)
--------------------
* changes to e-mail notification subcet to be more esaly parsable.
* fix: error with PublisherHealper when publishing to wast directory tree

v1.47.0 (2020.08.18)
--------------------
* Added ability for Zip files to append data to existing file

v1.46.3 (2020.08.12)
--------------------
* Fixed problems with backup function in SimpleFileOpsSafe

v1.46.2 (2020.08.09)
--------------------
* Fixed problems when PublisherHealper not processing json config files

v1.46.1 (2020.05.12)
--------------------
* SFTPHelper added ability to autorise SFTP connection with RSA private key file

v1.45.3 (2020.05.05)
--------------------
* bug fixes for AGServerHelperNTLM

v1.45.2 (2020.04.28)
--------------------
* aditional functionality for PublisherHealper

v1.45.1 (2019.15.12)
--------------------

* refactoring and aditional functionality for AGServerHelperNTLM. New functionality for working with permisions, roles and users
* refactoring and aditional functionality for PublisherHealper

v1.44.1 (2019.09.11)
--------------------

* Mor functionality for PublisherHealper module and coresponding functionality for JsonParamsHelper and xmlParamsHealper modules to support automated soulution publishing. New functionality further develops capabilities of automatic configuration file changing in CI/CD solutions.

v1.43.3 (2019.08.16)
--------------------

* MXDHelper module bug fixes

v1.43.2 (2019.07.26)
--------------------

* PublisherHealper module bug fixes

v1.43.1 (2019.07.19)
--------------------

* Some code cleanup and bug fixes
* PublisherHealper module has added functionality for updating Json parameter files

v1.42.1 (2019.05.24)
--------------------

* Added GISPythonToolBase module for geoprocessing tool operations and automation mechanisms for different operations
* Added PublisherHealper module for deployment operations and xmlParamsHealper for XML parameter file procedures
* AGServerHelperNTLM - added method for ArcGIS dataset name retrieval
* GISPythonModule - additional functionality for tool licence level check
* JsonParamsHelper - additional functionality for value update
* SysGISTools - restructured, multiple methods migrated to new GISPythonToolBase module
* SysTools_unittest - added encoding parameters
* Bug fix for TimerHelper

v1.41.1 (2019.01.03)
--------------------

* GDPSyncroniserHelper2 - added functionality for synchronising geodtabase tables with Python list objects

v1.40.2 (2018.11.24)
--------------------

* AGServerHelperNTLM.py added function to get rights group names for AGS services
* Added capabilities for SimpleFileOps and SimpleFileOpsSafe to CheckCreateClearDir - check if dir exist, creates it and clears in one function
* Added aditional support for outputting unicode text in script output

v1.40.1 (2018.09.26)
--------------------

* AGServerHelperNTLM.py added support for self generated SSL sites (Unverified SSL cases)
* Added capabilities for GDBHelper.py
* Bug fixes and added capabilities for GDPSyncroniserHelper2.py

v1.39.2 (2018.08.15)
--------------------

* Added aditional possibilities for SimpleFileOps.py

v1.39.1 (2018.07.29)
--------------------

* Added aditional possibilities for AGServerHelperNTLM.py

v1.38.1 (2018.07.20)
--------------------

* Bug fixes for GDPSyncroniserHelper2.py
* Added parameter EnvironmentName. Used for Error Email generation, to indicate Environment in with error ocured.
* Added SetupDefaultEnvironment.py module for fast environment setup.

v1.37.2 (2018.03.29)
--------------------

* Bug fixes for AGServerHelperNTLM

v1.37.1 (2018.03.29)
--------------------

* Bug fixes for ZipHelper and GISTools10

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
