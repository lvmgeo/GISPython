# -*- coding: utf-8 -*-
"""
     Timing module
"""

import datetime

class TimerHelper(object):
    """Class for easing the countdown procedures"""

    def __init__(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """
        self.StartTime = datetime.datetime.now()

    def TimerReset(self):
        """Reset the countdown

        Args:
            self: The reserved object 'self'
        """
        self.StartTime = datetime.datetime.now()


    def GetTime(self):
        """Get the elapsed time

        Args:
            self: The reserved object 'self'

        Returns:
            Output text as a string
        """
        TD = datetime.datetime.now() - self.StartTime
        return str(TD)

    def GetTimeReset(self):
        """Reset the elapsed time

        Args:
            self: The reserved object 'self'

        Returns:
            Output text as a string
        """
        TD = self.GetTime()
        self.TimerReset()
        return TD

class TimedSubprocess:
    """Class for providing a code block with timing capabilities"""

    def __init__(self, Tool, txt, lvl=1):
        """Class initialization procedure
        Args:
            self: The reserved object 'self'
            Tool: Reference to the GISTools10 object
            txt: Output text
            lvl: Sublevel
        """
        self.StartTime = datetime.datetime.now()
        self.Tool = Tool
        self.txt = txt
        self.T = TimerHelper()
        self.prefix = ""
        for i in range(0, lvl-1):
            self.prefix += '    '
    def __enter__(self):
        """With statement opening procedure
        Args:
            self: The reserved object 'self'
        """
        self.Tool.AddMessage(u'\n\n{0}------------------------\n{0}>>>> Begin {1} - {2}\n{0}------------------------\n'.format(self.prefix, self.txt, self.Tool.MyNow()))
        return self.Tool.callGP
    def __exit__(self, type, value, traceback):
        """With statement closing procedure
        Args:
            self: The reserved object 'self'
        """
        self.Tool.AddMessage(u'\n{0}------------------------\n{0}>>>> End {1} - {2}\n{0}------------------------\n'.format(self.prefix, self.txt, self.T.GetTimeReset()))
