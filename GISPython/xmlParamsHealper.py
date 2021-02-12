# -*- coding: utf-8 -*-
"""
     Module for xml parameter file procedures
"""

import os
import codecs
from lxml import etree
from collections import OrderedDict

utf8_parser = etree.XMLParser(encoding='utf-8')

class XMLParams(object):
    """xml parameter reading support class"""
    def __init__(self, Tool, ConfigFolder, ConfigFile):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            Tool: GISPythonTool (Optional)
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
        self.Params = []

    def GetParams(self):
        """Get parameters from the parameter file

        Args:
            self: The reserved object 'self'
        """
        with open(self.ConfigPath, 'r') as xmlfile:
            xmllines = xmlfile.readlines()
        doc = etree.ElementTree(etree.XML("".join(xmllines)))
        self.Params = doc
        return self.Params

    def WriteParams(self):
        """Save parameters in the parameter file

        Args:
            self: The reserved object 'self'
        """
        with open(self.ConfigPath, 'w') as xmlfile:
            # xmlString = etree.tostring(self.Params, pretty_print=True, method="xml", xml_declaration=True, encoding="utf-8")
            self.Params.write(xmlfile, pretty_print=True, method="xml", xml_declaration=True, encoding="utf-8")


    def UpdateValueByPath(self, path, Value, index = 0, isString = False):
        elem = self.Params
        if isString:
            elem.xpath(path)[index].append(etree.fromstring(Value))
        else:
            elem.xpath(path)[index].text = Value

    def AppendValueByPath(self, path, key, Value, attrib, index = 0, isString = False):
        elem = self.Params
        elem = elem.xpath(path)[index]
        if key==None:
            node = elem
        else:
            node = etree.SubElement(elem, key, attrib)
        if isString:
            node.append(etree.fromstring(Value))
        else:
            node.text = Value

    def UpdateAtributeByPath(self, path, atribute, Value, index = 0):
        elem = self.Params
        elem.xpath(path)[index].attrib[atribute] = Value

    def GetValueByPath(self, path, namespaces='#'):
        elem = self.Params
        if namespaces == '#':
            elem = elem.xpath(path)[0].text
        else:
            elem = elem.xpath(path, namespaces=namespaces)[0].text
        return elem

    def GetAtributeByPath(self, path, atribute, namespaces='#'):
        elem = self.Params
        if namespaces == '#':
            elem = elem.xpath(path)[0].attrib[atribute]
        else:
            elem = elem.xpath(path, namespaces=namespaces)[0].attrib[atribute]
        return elem
