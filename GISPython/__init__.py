# -*- coding: utf-8 -*-
"""
     Module for the package definition
"""

import os
import SysGISToolsSysParams

if __name__ == "__main__":
    """
        Execution of the module
    """
    print(u"""
    Hello!

    This is GISPython for ArcGIS 10.3.1.

    Version: """ + SysGISToolsSysParams.Version + u"""

    Author: LVM GEO

    Platform contains following additional modules:
    """)
    # Get the list of all python modules in GISPython folder
    filenames = [f for f in os.listdir(os.path.dirname(os.path.abspath(__file__))) if (os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), f)) and not f[0:3].upper() == "SYS" and f[-3:].upper() == '.PY' and f.upper() != 'MYERROR.PY' and f.upper() != 'GISPYTHONTOOL.PY' and f.upper() != 'GISPYTHONMODULE.PY' and f.upper() != '__INIT__.PY')]
    for fl in filenames:
            print('             ' + fl)
