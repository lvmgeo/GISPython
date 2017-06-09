# -*- coding: utf-8 -*-
"""
    Test procedure module
"""

import unittest
import GISPythonModule

class Pr(object):
    """Defines test parameters"""
    OutDir = 'C:\\GIS\\Log\\Outlog\\' # Output file directory
    OutDirArh = 'C:\\GIS\\Log\\Outlog\\Archive\\' # Output file archive directory
    ErrorLogDir = 'C:\\GIS\\Log\\ErrorLog\\' # Error output file directory
    ErrorLogDirArh = 'C:\\GIS\\Log\\ErrorLog\\Archive\\' # Error output file archive directory

class GISTools_unittest(unittest.TestCase):
    """GEOPython unit test class"""

    def setUp(self):
        """The Test setting up procedure"""
        print u"Preparing for tests..."
        self.Module = GISPythonModule.GISPythonModule('Unittest', Pr)
        self.Module.initModule()
        #don't catch errors in the file
        return super(GISTools_unittest, self).setUp()

    def tearDown(self):
        """"The Test tear down - cleaning up objects after test"""
        print u"Cleaning up after tests..."
        self.Module.MyDispose()
        return super(GISTools_unittest, self).tearDown()

    def test_Tool_init(self):
        """Check if it is possible to get the geoprocessor object"""
        print u"Check if it is possible to get the geoprocessor object ... OK"

    def test_shellRun(self):
        """Check the shell execution commands"""
        self.Module.Tool.runShell("Dir")
        print u"Check if it is possible to get the geoprocessor object ... OK"

if __name__ == "__main__":
    print ""
    unittest.main()
    raw_input("Press Enter to continue...")
