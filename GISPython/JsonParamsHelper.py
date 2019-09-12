# -*- coding: utf-8 -*-
"""
     Module for Json parameter file procedures
"""

import os
import codecs
import simplejson as json
from collections import OrderedDict

class JsonParams(object):
    """Json parameter reading support class"""
    def __init__(self, Tool, ConfigFolder, ConfigFile):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            Tool: GEOPython tool (optional)
            ConfigFolder: Configuration file storing directory
            ConfigFile: Name of the configuration file (without extension)
        """
        self.Tool = Tool
        self.ConfigFolder = ConfigFolder
        self.ConfigFile = ConfigFile
        if not Tool == None:
            self.ConfigPath = os.path.join(self.Tool.ExecutePatch, ConfigFolder, ConfigFile)
        else:
            if not ConfigFolder == None:
                self.ConfigPath = os.path.join(ConfigFolder, ConfigFile)
            else:
                self.ConfigPath = ConfigFile
        if not self.ConfigPath.lower()[-4:] == "json":
            self.ConfigPath = self.ConfigPath + '.json'
        self.Params = []

    def GetParams(self):
        """Get parameters from the parameter file

        Args:
            self: The reserved object 'self'
        """
        f = codecs.open(self.ConfigPath, 'r', 'utf-8')
        JsonString = f.read()
        f.close()
        J = json.loads(JsonString, object_pairs_hook=OrderedDict)
        self.Params = J
        return self.Params

    def WriteParams(self, sort_keys=True):
        """Save parameters in the parameter file

        Args:
            self: The reserved object 'self'
        """
        JsonString = json.dumps(self.Params, sort_keys, indent=4 * ' ')
        f = codecs.open(self.ConfigPath, 'w', 'utf-8')
        f.write(JsonString)
        f.close()

    def UpdateValueByPath(self, path, Value, valueIsStringJson = False):
        elem = self.Params

        if valueIsStringJson:
            Value = json.loads(Value, object_pairs_hook=OrderedDict)

        pathList = path.strip("\\").split("\\")
        for key in pathList[:-1]:
                elem = self.__get_sub_element__(elem, key)
        LastKey = pathList[-1:][0]

        elem[LastKey] = Value

    def AppendValueByPath(self, path, key, Value, valueIsStringJson = False):
        elem = self.Params

        if valueIsStringJson:
            Value = json.loads(Value, object_pairs_hook=OrderedDict)
            
        if not path == '':
            pathList = path.strip("\\").split("\\")
            for pathkey in pathList:
                    elem = self.__get_sub_element__(elem, pathkey)

        if isinstance(elem, list): 
            elem.insert(key, Value)
        else:
            elem[key] = Value

    def GetValueByPath(self, path):
        elem = self.Params
        pathList = path.strip("\\").split("\\")
        for key in pathList:
                elem = self.__get_sub_element__(elem, key)

        return elem

    def __get_sub_element__(self, element, key):
        position = 0
        if key.find('[')>-1 and key.find(']')>-1:
            position = int(key.replace(']','').replace('[',''))
            return element[position]
        else:
            return element[key]