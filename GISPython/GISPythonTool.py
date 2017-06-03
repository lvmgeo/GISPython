# -*- coding: utf-8 -*-
"""
     Module defines abstract classes for the ESRI Toolbox tool definition
"""

class GISPythonTool(object):
    """Class which helps to create an ArcGIS Toolbox"""
    def __init__(self):
        """Define the tool (tool name is the class name)"""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Determines if the tool is licenced for execution"""
        return True

    def updateParameters(self, parameters):
        """This method is called in case the parameters are changed,
        and is used for setting up the parameters
        """
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateParameters()

    def updateMessages(self, parameters):
        """This method is called after an inner validation,
        and is intended for carrying out an additional validations
        """
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateMessages()

    def execute(self, parameters, messages):
        """Executes a tool"""
        raise NotImplementedError

class ToolValidator(object):
    """Class for validating the tool's parameter values and controlling
    the behavior of the tool's dialog.
    """
    def __init__(self, parameters):
        """Setup arcpy and the list of the tool's parameters."""
        self.params = parameters

    def initializeParameters(self):
        """Refine properties of the tool's parameters. This method is
        called when the tool is opened.
        """
        return

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed.
        """
        return

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation.
        """
        return
