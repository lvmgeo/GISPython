# -*- coding: utf-8 -*-
"""
     Module for Json parameter file procedures
"""

import os
import codecs
import simplejson as json

class JsonParams(object):
    """Json parameter reading support class"""
    def __init__(self, Tool, ConfigFolder, ConfigFile):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            Tool: GEOPython tool
            ConfigFolder: Configuration file storing directory
            ConfigFile: Name of the configuration file (without extension)
        """
        self.Tool = Tool
        self.ConfigFolder = ConfigFolder
        self.ConfigFile = ConfigFile
        self.ConfigPath = os.path.join(self.Tool.ExecutePatch, ConfigFolder, ConfigFile + '.Json')
        self.Params = []

    def GetParams(self):
        """Get parameters from the parameter file

        Args:
            self: The reserved object 'self'
        """
        f = codecs.open(self.ConfigPath, 'r', 'utf-8')
        JsonString = f.read()
        f.close()
        J = json.loads(JsonString)
        self.Params = J
        return self.Params

    def WriteParams(self):
        """Save parameters in the parameter file

        Args:
            self: The reserved object 'self'
        """
        JsonString = json.dumps(self.Params, sort_keys=True, indent=4 * ' ')
        f = codecs.open(self.ConfigPath, 'w', 'utf-8')
        f.write(JsonString)
        f.close()
