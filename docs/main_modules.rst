Main modules
============

*GISPython* package core modules
   
GISPythonModule
---------------

*Main module, which contains frame for all  GISPython package modules. Module allows the code unification, and ensures the code execution from both the ArcGIS Desktop Python console and the Command Prompt.*

.. automodule:: GISPython.GISPythonModule
    :members:
    :undoc-members:
    :show-inheritance:

Examples
********
Executes the tool if it's to be executed within an another Python tool::

	from  GISPython import TimerHelper
	import OnlineCompress

	with TimerHelper.TimedSubprocess(Tool, u'Compress DB'): # Adds a message to the tool output
		with TimerHelper.TimedSubprocess(Tool, u'disconnect users from DB', 2): # Adds a message to the tool output
			self.Tool.RunSQL('KillUsers', Pr.u_sde, Pr.p_sde) # Runs custom SQL script
		OnlineCompress.MainModule(None, False).runInsideJob(Tool) # Runs SDE Compression procedure from OnlineCompress module (custom geoprocessing module)
	
GISPythonTool
-------------

*Module defines abstract classes for the ESRI Toolbox tool definition and contains functions which helps to create an ArcGIS Toolbox, validates the tool's parameter values and controls a behavior of the tool's dialog.*

.. automodule:: GISPython.GISPythonTool
    :members:
    :undoc-members:
    :show-inheritance:
	
Examples
********
Define parameters in ESRI Python toolbox::

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

	
SysGISTools
-----------

*Base module which contains GISPython scripting framework, logging, error processing and automation mechanisms for different operations, and module and interface base classes.*

.. automodule:: GISPython.SysGISTools
    :members:
    :undoc-members:
    :show-inheritance:
	
Examples
********
Run a script from Shell with parameters::

	Tool = self.Tool
	# Executes your custom process script (mainly maintenance scripts) within runShell function,
	# which implements _runProcess function (message output in terminal window).
	# Function executes script seperately from main process (Detached=True) and indicates, 
	# that the errors doesn't have to be logged (noErr=True).
	Tool.runShell('SomeProcess.py', Detached = True, noErr = True)
	time.sleep(10) # after 10 seconds launch another runShell process
	
Executes a custom SQL script file (only Oracle sqlplus supported)::

	from GISPython import TimerHelper

	Tool = self.Tool
	# Executes process from SQL file
	with TimerHelper.TimedSubprocess(self.Tool, u'datu atlasi no nogabaliem'): # Adds a message to the tool output
		Tool.RunSQL('LoadSomeDataFromTable') # Runs SQL file within RunSQL function, which implements GetSQL function (gets the SQL file location)
		
Duplicates path seperator symbol '\' for external execution compatibility::

	from GISPython import SimpleFileOps
	from GISPython import TimerHelper

	Tool = self.Tool
	# Your code
	with TimerHelper.TimedSubprocess(Tool, u'prepare environment'): # Adds a message to the tool output
		DirHelper = SimpleFileOps.SimpleFileOps(Tool) # Set variable for SimpleFileOps module functions
		tmpFolder = os.path.join(Pr.TmpFolder, "Soil") # Set tmp folder path
		# Your code
		Tool.AddMessage(u'\n        ...delete previous tmp data') # Add tool output message
		DirHelper.CheckCreateDir(Tool.CorrectStr(tmpFolder)) # Check/create tmp directory (with modified path seperators)
		DirHelper.ClearDir(Tool.CorrectStr(tmpFolder)) # Clear tmp directory (with modified path seperators)
	
SysGISToolsSysParams
--------------------

.. automodule:: GISPython.SysGISToolsSysParams
    :members:
    :undoc-members:
    :show-inheritance:
	
SysTools_unittest
-----------------

.. automodule:: GISPython.SysTools_unittest
    :members:
    :undoc-members:
    :show-inheritance:
	
.. toctree::
   :maxdepth: 4