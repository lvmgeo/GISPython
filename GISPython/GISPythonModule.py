# -*- coding: utf-8 -*-
"""
     Module for the GISPython module frame and code unification
"""

import sys
import os
import traceback
import SysGISTools
import MailHelper
import MyError

class GISPythonModule(object):
    """Interface class for all the GISPython modules. Interface class allows
    the code unification, and ensures the code execution from both the
    ArcGIS Desktop Python console and the Command Prompt.

    Standalone tool execution:
        SetName('Tool Name')
        DoJob()

    The tool executes within an another tool:
        SetTool(reference to SysGISTools.GISTools10)
        Get the tool name with the command 'PrintText()'
        mainModule()
    """
    def __init__(self, ToolName, SysGISParams, ExecutePatch=__file__, statusMailRecipients=[], errorMailRecipients=[]):
        """Initialize the tool and the tool parameters

        Args:
            self: The reserved object 'self'
            ToolName: Tool name
            SysGISParams: GISPython parameter module
            ExecutePatch: Module execution path
            statusMailRecipients: List with status e-mail message recipients
            errorMailRecipients: List with error e-mail message recipients
        """
        self.ToolName = ToolName
        self.Pr = SysGISParams
        self.ExecutePatch = os.path.dirname(os.path.realpath(ExecutePatch))
        if  hasattr(self.Pr, 'EnableStatusMail'):
            self.DoMail = self.Pr.EnableStatusMail
        else:
            self.DoMail = False
        self.DoMailOutput = False
        self.DoMailErrOutput = False
        if self.DoMail:
            self.statusMailRecipients = statusMailRecipients
            if  hasattr(self.Pr, 'MailOutputRecipientsAlways'):
                self.statusMailRecipients = self.statusMailRecipients + self.Pr.MailOutputRecipientsAlways
            self.errorMailRecipients = errorMailRecipients
            if  hasattr(self.Pr, 'MailErrorRecipientsAlways'):
                self.errorMailRecipients = self.errorMailRecipients + self.Pr.MailErrorRecipientsAlways
            if self.statusMailRecipients != []:
                self.DoMailOutput = True
            if self.errorMailRecipients != []:
                self.DoMailErrOutput = True

    def runInsideJob(self, Tool):
        """Procedure executes the tool, if it's to be executed within an another Python tool

        Args:
            self: The reserved object 'self'
            Tool: The tool name to execute
        """
        self.SetTool(Tool)
        self.PrintText()
        self.mainModule()

    def mainModule(self):
        """Rewritable procedure which contains the logic of the module
        """
        raise NotImplementedError

    def initModule(self):
        """Procedure which initializes the GISPython environment, if the tool runs as a standalone tool
        """
        self.Tool = SysGISTools.GISTools10(self.ToolName, self.Pr)
        sys.stderr = self.Tool.fLog
        self.Tool.ExecutePatch = self.ExecutePatch

    def SetTool(self, Tool):
        """Sets up the GISPython environment object, if the tool runs within an another tool
        """
        self.Tool = Tool

    def PrintText(self):
        """The auxiliary procedure for the tool name output
        """
        self.Tool.AddMessage("--------------------------------------------")
        self.Tool.AddMessage(self.ToolName)
        self.Tool.AddMessage("--------------------------------------------")

    def MyEnd(self):
        """Procedure for the tool end message output, if the tool runs as a standalone tool
        """
        self.Tool.MyEnd()

    def MyDispose(self):
        """Procedure which closes the tool environment after running it (in case the tool runs as a standalone tool)
        """
        self.Tool.MyDispose()

    def DoJob(self):
        """Procedure which runs the tool with environment preparation and deletion (in case the tool runs as a standalone tool)
        """
        try:
            self.initModule()
            self.mainModule()
            self.MyEnd()
            if self.DoMailOutput:
                MailHelper.GISPythonMailHelper(self.Pr, self.statusMailRecipients, unicode.format(u'{0} - {1}', self.ToolName, self.Tool.MyNow()), self.Tool.OutputStr)
            if self.DoMailErrOutput:
                if not self.Tool.OutputErrStr == u'':
                    MailHelper.GISPythonMailHelper(self.Pr, self.errorMailRecipients, unicode.format(u'Error {0} - {1}', self.ToolName, self.Tool.MyNow()), self.Tool.OutputErrStr)
            self.MyDispose()
        except Exception, e:
            # If an error occurred, print line number and error message
            tb = sys.exc_info()
            orgLine = "Line %i" % tb[2].tb_lineno
            orgTraceback = unicode(traceback.format_exc(), errors='ignore')
            if hasattr(self, 'Tool'):
                try:
                    if not (self.Tool.State == "Disposed" or self.Tool.gp == None):
                        self.Tool.AddWarning(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                        try:
                            self.Tool.AddWarning(u'Raw tool error {0} - {1}'.format(self.ToolName, self.Tool.MyNow()))
                        except:
                            None
                        self.Tool.AddWarning(orgLine)
                        self.Tool.AddError(orgTraceback)
                        self.Tool.AddWarning(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                        self.Tool.AddWarning(u'GP tool output')
                        self.Tool.AddWarning(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                        self.Tool.OutputErrors()
                        if self.DoMailErrOutput:
                            if self.Tool.OutputErrStr != u'':
                                MailHelper.GISPythonMailHelper(self.Pr, self.errorMailRecipients, unicode.format(u'Error {0} - {1}', self.ToolName, self.Tool.MyNow()), self.Tool.OutputErrStr)
                    else:
                        print(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                        print(u'Raw tool error {0}'.format(self.ToolName))
                        print(orgLine)
                        print(orgTraceback)
                        print(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                        if self.DoMailErrOutput:
                            MailHelper.GISPythonMailHelper(self.Pr, self.errorMailRecipients, unicode.format(u'Critical error   {0}', self.ToolName), orgLine + '\n' + orgTraceback)
                        raise
                except Exception, ex:
                    print(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                    print(u'Raw tool error {0}'.format(self.ToolName))
                    print(orgLine)
                    print(orgTraceback)
                    print(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                    if self.DoMailErrOutput:
                        MailHelper.GISPythonMailHelper(self.Pr, self.errorMailRecipients, unicode.format(u'Critical error {0}', self.ToolName), orgLine + '\n' + orgTraceback)
                    raise e
            else:
                print(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                print(u'Raw tool error {0}'.format(self.ToolName))
                print(orgLine)
                print(orgTraceback)
                print(r'-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                if self.DoMailErrOutput:
                    MailHelper.GISPythonMailHelper(self.Pr, self.errorMailRecipients, unicode.format(u'Critical error {0}', self.ToolName), orgLine + '\n' + orgTraceback)
                raise

class GISPythonModuleArgsHelper(object):
    """Class for handling the argument passing for the module in three different places:

    1. In the class initialization process.
    2. In the arguments.
    3. In the "main" operation call.
    """
    def __init__(self, InitValue=None):
        self.argumentValue = None
        self.initValue = None
        self.mainModuleValue = None
        self.SetInitValue(InitValue)

    def processArgument(self, argumentNumber=1):
        """Procedure processes a parameter acquisition from the argument

        Args:
            self: The reserved object 'self'
            argumentNumber: Argument from which to read the data
        """
        if len(sys.argv) > argumentNumber:
            self.argumentValue = sys.argv[argumentNumber]
            if self.argumentValue == '#':
                self.argumentValue = None


    def SetInitValue(self, value):
        """Procedure processes a parameter setup from the tool initialization procedure

        Args:
            self: The reserved object 'self'
            value: Setup value
        """
        self.initValue = value
        if self.initValue == '#':
            self.initValue = None

    def SetMainModuleValue(self, value):
        """Procedure processes a parameter setup from the base module of the tool

        Args:
            self: The reserved object 'self'
            value: Setup value
        """
        self.mainModuleValue = value
        if self.mainModuleValue == '#':
            self.mainModuleValue = None

    def GetResultValue(self, asBool=False, Default=None):
        """Procedure makes a choice from the given attributes

        Args:
            self: The reserved object self
            value: Setup value
        """
        candidate = Default

        if self.argumentValue != None:
            candidate = self.argumentValue
        else:
            if self.mainModuleValue != None:
                candidate = self.mainModuleValue
            else:
                if self.initValue != None:
                    candidate = self.initValue
        if asBool:
            if candidate == None:
                candidate = False
            elif unicode(candidate).upper() == u'TRUE':
                candidate = True
            elif unicode(candidate).upper() == u'FALSE':
                candidate = False
            else:
                raise MyError.MyError(u'Cannot convert the value {0} to a boolean'.format(candidate))

        return candidate
