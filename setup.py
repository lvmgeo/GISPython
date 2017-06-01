from setuptools import setup
import os
import shutil
import re

# Copy files from GISPython directory to geopythoncore (except __init__.py)
src = r'C:\TFS\GEOPython10-GIT\GEOPython10\GISPython'
dest = 'C:\TFS\GEOPython10-GIT\GEOPython10\geopythoncore\GISPython'
excl = '__init__.py'

baseFileList = [bf for bf in os.listdir(src) if not (bf.endswith('pyc') or bf == excl)]
PShellList = os.listdir(os.path.join(src, 'PShell'))

for bf in baseFileList:
    srcFile = os.path.join(src, bf)
    if bf == 'PShell':
        for pf in PShellList:
            shutil.copy(os.path.join(src, 'PShell', pf), os.path.join(dest, bf))
    else:
        shutil.copy(srcFile, dest)

def get_version():
    """Get version number from SysGISToolsSysParams file"""
    versFile = 'GISPython\\SysGISToolsSysParams.py'
    versFDir = os.path.dirname(os.path.abspath(__file__))
    versionpath = os.path.join(versFDir, versFile)
    fileRead = open(versionpath, 'rt').readlines()
    vsre = r"^Version = ['\"]([^'\"]*)['\"]"
    for line in fileRead:
        mo = re.search(vsre, line, re.M)
        if mo:
            return str(mo.group(1)[24:])

setup(
    name = 'GISPython',
    version = get_version(), # version number according to PEP440 https://www.python.org/dev/peps/pep-0440/
    description = 'Additional tools for administering and automating different arcpy geoprocessing operations. Package is intended for use with ArcGIS 10.2.1 and later (has been tested on ArcGIS 10.4)', # short package description
    long_description = 'For readme see GitHub https://bitbucket.org/arturspd/geopythontest', # if needed (entire documentation)
    url = 'https://bitbucket.org/arturspd/geopythontest', # GitHub url
    # url = 'https://localhost:8081/simple', # private url
    author = 'LVM BSR', # author
    author_email = '', # email
    license = 'LICENSE.txt', # license

    # classifiers for PyPi: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Project development status
        'Development Status :: 4 - Beta',
        # Intended audience and topic
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        # License https://choosealicense.com/
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        # Operating system
        'Operating System :: Microsoft :: Windows',

        # Specify the Python versions you support here.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords = ['ArcGIS', 'arcpy', 'automation'], # keywords (string or list of strings)
    packages = ["GISPython"], # packages to install
    include_package_data = True,
    install_requires = ['paramiko>=2.1.2', 'simplejson>=3.10.0'], # list of packages required in project (these will be installed by pip)

    # give entry points
    # first refactor code like this
    #def main():  # Entry point for scripts
      ## Parse command line args 
      ## Do a bunch of stuff
 
    # if __name__ == "__main__":
    #   main()

    entry_points = {'console_scripts': [
        'GISPython = __init__:main'
        ]
    },
)