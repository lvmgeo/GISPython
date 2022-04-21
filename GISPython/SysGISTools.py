# -*- coding: utf-8 -*-
"""
    GIS function support module
"""
import GDBHelper
import GISPythonToolBase
import codecs

class GISTools10(GISPythonToolBase.GISPythonToolBase):
    """Class for storing the auxiliary batch processing and GIS geoprocesing functions"""
    def __init__(self, ToolName, Params, licenceLevel = "arceditor"):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            ToolName: Name of the tool (used for output)
            Params: parameter object
            licenceLevel: arcinfo, arceditor, arcview, arcserver, arcenginegeodb, or arcengine
        """
        super(GISTools10, self).__init__(ToolName, Params)

        if licenceLevel == "arcinfo":
            print(u'...Using licence level : ' + licenceLevel)
            import arcinfo
        elif licenceLevel == "arceditor":
            print(u'...Using licence level : ' + licenceLevel)
            import arceditor
        elif licenceLevel == "arcview":
            print(u'...Using licence level : ' + licenceLevel)
            import arcview
        elif licenceLevel == "arcserver":
            print(u'...Using licence level : ' + licenceLevel)
            import arcserver
        elif licenceLevel == "arcenginegeodb":
            print(u'...Using licence level : ' + licenceLevel)
            import arcenginegeodb
        elif licenceLevel == "arcengine":
            print(u'...Using licence level : ' + licenceLevel)
            import arcengine
        else:
            print(u'...Incorect licence suplied - using : arceditor')
            import arceditor
            
        import arcpy # arcpy variables
        self.gp = arcpy
        if hasattr(Params, 'SetLogHistory'):
            arcpy.SetLogHistory(Params.SetLogHistory)
        else:
            arcpy.SetLogHistory(False)
        self.GDBHelper = GDBHelper.GDBHelper(self.gp)
        self.SR = MySR()

        # Set up Logging
        LogDir = self.Pr.ErrorLogDir
        LogDirArh = self.Pr.ErrorLogDirArh
        OutDir = self.Pr.OutDir
        OutDirArh = self.Pr.OutDirArh

        try:
            self.AchiveFiles(LogDir, LogDirArh, ToolName, False)
        except Exception, err:
            print(u'Error archiving errlog files')
            if hasattr(err, 'strerror'):
                if hasattr(err, 'strerror'):
                    print(err.strerror)
                else:
                    print('{}'.format(err))
            else:
                print(err.message)
        try:
            self.AchiveFiles(OutDir, OutDirArh, ToolName, False)
        except Exception, err:
            print(u'Error archiving outlog files')
            if hasattr(err, 'strerror'):
                if hasattr(err, 'strerror'):
                    print(err.strerror)
                else:
                    print('{}'.format(err))
            else:
                print(err.message)
        self.error_log_path = LogDir + '\\' + self.ToolName + self.MyNowFile() + '.errlog'
        self.fLog = codecs.open(self.error_log_path, encoding='utf-8', mode='w')
        self.out_log_path = OutDir + '\\' + self.ToolName + self.MyNowFile() + '.outlog'
        self.fOut = codecs.open(self.out_log_path, encoding='utf-8', mode='w')
        self.fSQL = OutDir + '\\' + self.ToolName + self.MyNowFile() + 'SQL.outlog'

        self.AddMessage(u'\n==================================================')
        self.AddMessage(r'//////////////////////////////////////////////////')
        self.AddMessage(u'Executing the tool ' + ToolName + u' ' + self.MyNow())
        self.AddMessage(r'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
        self.AddMessage(u'==================================================\n')

    def callGP(self, functionName, *args):
        """Function to call the arcPy GP functions with automatic output messge display and output result returning

        Args:
            self: The reserved object 'self'
            functionName: Name of the arcPy GP function
            args: arguments as Tuple
        """
        gpOutput = self.callGPSilent(functionName, *args)
        self.OutputMessages()
        return gpOutput

    def callGPSilent(self, functionName, *args):
        """Function to call the arcPy GP functions without output

        Args:
            self: The reserved object 'self'
            functionName: Name of the arcPy GP function
            args: arguments as Tuple
        """
        gpFunction = getattr(self.gp, functionName)
        rezult = gpFunction(*args)
        if rezult.outputCount > 0:
            gpOutput = rezult.getOutput(0)
        else:
            gpOutput = None
        return gpOutput

    def MyEnd(self):
        """End of the process

        Args:
            self: The reserved object 'self'
        """
        super(GISTools10, self).MyEnd()
        self.fOut.close()
        self.fLog.close()

    def OutputMessages(self, ErrorSeverity=2):
        """Procedure to output messages stored in the GP object

        Args:
            self: The reserved object 'self'
            ErrorSeverity: Maximum Severity to report as error
        """
        self.AddMessage('\n--------------------------------------------')
        maxSeverity = self.gp.GetMaxSeverity()
        for i in range(0, self.gp.GetMessageCount()):
            self.gp.AddReturnMessage(i)
            #self.gp.AddMessage(self.gp.GetMessage(i))
            self.fOut.write(self.gp.GetMessage(i))
            self.OutputStr += self.gp.GetMessage(i)
            self.fOut.write('\n')
            self.OutputStr += '\n'
            self.fOut.flush()
            if maxSeverity >= ErrorSeverity:
                self.fLog.write(self.gp.GetMessage(i))
                self.OutputErrStr += self.gp.GetMessage(i)
                self.fLog.write('\n')
                self.OutputErrStr += '\n'
                self.fLog.flush()
        self.AddMessage('--------------------------------------------')

    def OutputErrors(self):
        """Procedure to output messages and errors stored in the GP object.
        !!! Depricated - Left for backwards compatibility - use OutputMessages with ErrorSeverity 0 !!!

        Args:
            self: The reserved object 'self'
        """
        self.AddMessage('')
        self.AddMessage('--------------------------------------------')
        for i in range(0, self.gp.GetMessageCount()):
            self.gp.AddReturnMessage(i)
            self.fOut.write(self.gp.GetMessage(i))
            self.OutputStr += self.gp.GetMessage(i)
            self.fOut.write('\n')
            self.OutputStr += '\n'
            self.fOut.flush()
            self.fLog.write(self.gp.GetMessage(i))
            self.OutputErrStr += self.gp.GetMessage(i)
            self.fLog.write('\n')
            self.OutputErrStr += '\n'
            self.fLog.flush()
        self.AddMessage('--------------------------------------------')

    def AddMessage(self, strMessage, newline=True):
        """Procedure for a message output (screen, logfile and if necessary e-mail)

        Args:
            self: The reserved object 'self'
            strMessage: Output message text
            newline: Flag that marks that the output must be continued in a new line
        """
        if strMessage == None:
            strMessage = ''
        if not isinstance(strMessage, unicode):
            if not isinstance(strMessage, str):
                strMessage = str(strMessage)
        if strMessage[-1:] == '\n':
            strMessage = strMessage[0:-1]
        try:
            self.fOut.write(strMessage)
            self.OutputStr += strMessage
        except:
            self.fOut.write(self._tryCovertStringEncoding(strMessage))
            self.OutputStr += self._tryCovertStringEncoding(strMessage)

        try:
            self.gp.AddMessage(strMessage)
        except:
            print strMessage
        if newline == True:
            self.fOut.write('\n')
            self.OutputStr += '\n'
        self.fOut.flush()

    def AddError(self, strMessage, newline=True):
        """Procedure for the GP object error message output (screen, logfile and if necessary e-mail)

        Args:
            self: The reserved object 'self'
            strMessage: Output message text
        """
        if strMessage == None:
            strMessage = ''
        if not isinstance(strMessage, unicode):
            if not isinstance(strMessage, str):
                strMessage = str(strMessage)
        if strMessage[-1:] == '\n':
            strMessage = strMessage[0:-1]
        try:
            self.gp.AddError(strMessage)
        except:
            print strMessage
        try:
            self.fLog.write(strMessage)
            self.OutputErrStr += strMessage
        except:
            self.fLog.write(self._tryCovertStringEncoding(strMessage))
            self.OutputErrStr += self._tryCovertStringEncoding(strMessage)
        if newline == True:
            self.fLog.write('\n')
            self.OutputErrStr += '\n'
        self.fLog.flush()
        try:
            self.fOut.write(strMessage)
            self.OutputStr += strMessage
        except:
            self.fOut.write(self._tryCovertStringEncoding(strMessage))
            self.OutputStr += self._tryCovertStringEncoding(strMessage)
        if newline == True:
            self.fOut.write('\n')
            self.OutputStr += '\n'
        self.fOut.flush()

    def AddWarning(self, strMessage):
        """Procedure for the GP object warning message output (screen, logfile and if necessary e-mail)

        Args:
            self: The reserved object 'self'
            strMessage: Output message text
        """
        if strMessage == None:
            strMessage = ''
        if not isinstance(strMessage, unicode):
            if not isinstance(strMessage, str):
                strMessage = str(strMessage)
        if strMessage[-1:] == '\n':
            strMessage = strMessage[0:-1]
        try:
            self.gp.AddWarning(strMessage)
        except:
            print strMessage
        try:
            self.fLog.write(strMessage)
            self.OutputErrStr += strMessage
        except:
            self.fLog.write(self._tryCovertStringEncoding(strMessage))
            self.OutputErrStr += self._tryCovertStringEncoding(strMessage)
        self.fLog.write('\n')
        self.OutputErrStr += '\n'
        self.fLog.flush()
        try:
            self.fOut.write(strMessage)
            self.OutputStr += strMessage
        except:
            self.fOut.write(self._tryCovertStringEncoding(strMessage))
            self.OutputStr += self._tryCovertStringEncoding(strMessage)
        self.fOut.write('\n')
        self.OutputStr += '\n'
        self.fOut.flush()



class MySR():
    """Class for storing often used coordinate system parameters"""
    def __init__(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """
        self.LKS92_0 = "PROJCS['LKS_1992_Latvia_TM_0',GEOGCS['GCS_LKS_1992',DATUM['D_Latvia_1992',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',24.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
        self.LKS92 = "PROJCS['LKS_1992_Latvia_TM',GEOGCS['GCS_LKS_1992',DATUM['D_Latvia_1992',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',-6000000.0],PARAMETER['Central_Meridian',24.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
        self.WebMercator = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]"
        self.WGS84 = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
