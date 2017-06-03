# -*- coding: utf-8 -*-
"""
     Rar file operations module
"""

import patoolib

class RarHelper:
    """Class for easing the Rar file operations"""

    def __init__(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """

    def ExtractRarFile(self, RarFileName, destPath):
        """Rar file extraction procedure

        Args:
            self: The reserved object 'self'
            RarFileName: Extractable file path + name
            destPath: Destination path for extracted files
        """
        patoolib.extract_archive(RarFileName, outdir=destPath)
