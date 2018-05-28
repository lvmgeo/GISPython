# -*- coding: utf-8 -*-
"""
    Module for setting up an default environment
"""

import codecs, os

paramsFileSource = """# -*- coding: cp1257 -*-
'''
    Standard generated gispython params file
    see: http://gispython.readthedocs.io/en/latest/index.html
'''

import  GISPython.SysGISToolsSysParams
import os


# ---------------------------------------------------------------------------
# Basic parameters
# ---------------------------------------------------------------------------
Version =  GISPython.SysGISToolsSysParams.Version
OutDir = 'C:\\\\GIS\\\\Log\\\\Outlog\\\\' # Output file directory
OutDirArh = 'C:\\\\GIS\\\\Log\\\\Outlog\\\\Archive\\\\' # Output file directory archive
ErrorLogDir = 'C:\\\\GIS\\\\Log\\\\ErrorLog\\\\' # Error output file directory
ErrorLogDirArh = 'C:\\\\GIS\\\\Log\\\\ErrorLog\\\\Archive\\\\' # Error output file directory archive
TmpFolder = 'C:\\\\GIS\\\\tmp\\\\' # Temp directory
# DataFolder = 'C:\\\\GIS\\\\Data\\\\' # Directory for storing source data (not automaticaly created)
# BackupFolder = 'C:\\\\GIS\\\\Backup\\\\' # Directory for storing data backup (not automaticaly created)
encodingPrimary = 'cp1257' # Windows charset
encodingSecondary = 'cp775' # Windows Shell charset
SetLogHistory = False # enable or disable Geoprocessing history logging 
"""

sampleModule = """# -*- coding: utf-8 -*-
'''This sample code can be used as a template for gispython modules'''
import os

from  GISPython import GISPythonModule

import SysGISParams as Pr


#main class GISPythonModule
class MainModule (GISPythonModule.GISPythonModule):
    '''
        Main module
    '''
    def __init__(self):
        '''Class initialization'''
        modulename = os.path.splitext(os.path.basename(__file__))[0]
        GISPythonModule.GISPythonModule.__init__(self, modulename, Pr, __file__, licenceLevel = 'arceditor')

    def mainModule(self):
        '''
            Main procedure
            Args:
                self: The reserved object 'self'
        '''
        # initialization of default shortcuts - simplifies code usage
        Tool = self.Tool # gispython tools
        callGP = self.Tool.callGP  # ArcPy geoprocesing tools runner
        pj = os.path.join # shorter syntax for path joining
        arcpy = self.Tool.gp # already initialized arcpy

        Tool.AddMessage('\\nHello World!\\n ')


if __name__ == '__main__':
    '''default execution'''
    Module = MainModule()
    Module.DoJob()
"""

def CheckCreateDir(OutDirName):
        """Automation procedure which creates directory, in case it doesn't exist

        Args:
            self: The reserved object 'self'
            OutDirName: Output directory
        """
        if not os.path.exists(OutDirName):
            os.makedirs(OutDirName)
            print('...Directory "{0}" created'.format(OutDirName))
        else:
            print('...Directory "{0}" already exists'.format(OutDirName))

if __name__ == "__main__":
    '''default execution'''
    CheckCreateDir(r'C:\GIS')
    CheckCreateDir(r'C:\GIS\Log')
    CheckCreateDir(r'C:\GIS\GISPythonScripts')
    CheckCreateDir(r'C:\GIS\tmp')
    CheckCreateDir(r'C:\GIS\Log\Outlog')
    CheckCreateDir(r'C:\GIS\Log\Outlog\Archive')
    CheckCreateDir(r'C:\GIS\Log\ErrorLog')
    CheckCreateDir(r'C:\GIS\Log\ErrorLog\Archive')
    paramsFileName = r'C:\GIS\GISPythonScripts\SysGISParams.py'
    if os.path.exists(paramsFileName):
            print('...old params file found "{0}" ... will not be owerwriten'.format(paramsFileName))
    else:
        with codecs.open(paramsFileName, "w", "utf-8") as prFile:
            prFile.write(paramsFileSource)
            print('...params file created "{0}"'.format(paramsFileName))
    sampleFileName = r'C:\GIS\GISPythonScripts\sampleGISPythonModule.py'
    if os.path.exists(sampleFileName):
            print('...old sample file found "{0}" ... will not be owerwriten'.format(sampleFileName))
    else:
        with codecs.open(sampleFileName, "w", "utf-8") as smplFile:
            smplFile.write(sampleModule)
            print('...sample file created "{0}"'.format(sampleFileName))
