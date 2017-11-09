from setuptools import setup
import os
import re

def get_version():
    """Get version number from SysGISToolsSysParams file"""
    #versFile = 'GISPython\\SysGISToolsSysParams.py'
    versFile = os.path.join('GISPython', 'SysGISToolsSysParams.py') # os.path.join for Unix compatibility
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
    description = 'Additional tools for administering and automating different ArcPy and ArcGIS Server geoprocessing operations. Package is intended for use with ArcGIS 10.2.1 and later (has been tested on ArcGIS 10.4)', # short package description
    long_description = 'For readme see GitHub https://github.com/lvmgeo/GISPython', # if needed (entire documentation)
    url = 'https://github.com/lvmgeo/GISPython', # GitHub url
    author = 'LVM GEO', # author
    author_email = 'lvmGEOGit@lvm.lv', # email
    license = 'GPLv3', # license

    # classifiers for PyPi: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Project development status
        'Development Status :: 5 - Production/Stable',
        # Intended audience and topic
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules',
        # License https://choosealicense.com/
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Operating system
        'Operating System :: Microsoft :: Windows',

        # Specify the Python versions you support here.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords = ['ArcGIS', 'ArcPy', 'ArcGIS Server', 'automation'], # keywords (string or list of strings)
    packages = ["GISPython"], # packages to install
    include_package_data = True,
    install_requires = ['paramiko>=2.1.2', 'simplejson>=3.10.0', 'patool>=1.12', 'python-ntlm>=1.1.0'], # list of packages required in project (these will be installed by pip)

    # entry_points = {'console_scripts': [
        # 'GISPython = __init__:main'
        # ]
    # },
)