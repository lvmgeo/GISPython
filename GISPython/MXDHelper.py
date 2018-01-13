# -*- coding: utf-8 -*-
"""
     MXD hepler functions
"""

import TimerHelper
import GDBHelper
import os, sys, traceback

class MXDHelper:
    """Class for easing the MXD file operations"""

    def __init__(self, gp=None, Tool=None):
            """Class initialization procedure
                Args:
                    self: The reserved object 'self'
                    gp: ArcPy GP object
                    Tool: Reference to the GISTools10 object
            """
            if Tool == None:
                self.gp = gp
                self.isTool = False
            else:
                self.isTool = True
                self.gp = Tool.gp
                self.Tool = Tool
    
    def AddWarning(self, str):
        """Helper function to unify use of AddWarning with GISPython Tool or without"""
        if self.isTool:
            self.Tool.AddWarning(str)
        else:
            self.gp.AddWarning(str)
    
    def AddMessage(self, str):
        """Helper function to unify use of AddMessage with GISPython Tool or without"""
        if self.isTool:
            self.Tool.AddMessage(str)
        else:
            self.gp.AddMessage(str)

    def OutputMessages(self, ErrorSeverity=2):
        """Helper function to unify use of OutputMessages with GISPython Tool or without"""
        if self.isTool:
            self.Tool.OutputMessages(str)
        else:
            maxSeverity = self.gp.GetMaxSeverity()
            if maxSeverity > 1:
                self.gp.AddMessage('')
                self.gp.AddMessage('--------------------------------------------')
                for i in xrange(0, self.gp.GetMessageCount()):
                    self.gp.AddReturnMessage(i)
                self.gp.AddMessage('--------------------------------------------')

    def ChangeMXDSource(self, mxd, conn, difOutDir = False, outDir = "#", silent=False):
        """Changes MXD file connection and saves the file in user specified directory
            Args:
                self: The reserved object 'self'
                mxd: path to MXD,
                conn: new connection,
                difOutDir: is the output dir diferent from source (do the MXD be saved in thesame path ('TRUE'))
                outDir: directory to with to copy new MXD,
                silent: does the messages will be supressed"""

        T = TimerHelper.TimerHelper()
        if not silent == True:
            self.AddMessage(u'    Processing document [{0}]'.format(mxd))
        if not self.gp.Exists(mxd):
            self.AddWarning(u'MXD with path {0} has not been found'.format(MXD))
        else:
            if not silent == True:
                 self.AddMessage(u'        Document found')
            T.TimerReset()
            try:
                Doc = self.gp.mapping.MapDocument(mxd)
                if not silent == True: 
                    self.AddMessage(u'        Document opened - {0}'.format(T.GetTimeReset()))
                try:
                    Doc.replaceWorkspaces('', 'NONE', conn, 'SDE_WORKSPACE', True)
                    #Doc.findAndReplaceWorkspacePaths("", conn, True)
                    if not silent == True: 
                        self.AddMessage(u'        Document sources changed - {0}'.format(T.GetTimeReset()))
                    try:
                        if difOutDir == True:
                            sourceDir = os.path.basename(mxd)
                            outPath = mxd.replace(sourceDir, outDir)
                            outDir = os.path.dirname(outPath)
                            if not os.path.exists(outDir):
                                os.makedirs(outDir)
                            Doc.saveACopy(outPath)
                        else:
                            Doc.save()
                        del Doc
                        if not silent == True: 
                            self.AddMessage(u'        Document saved - {0}'.format(T.GetTimeReset()))
                    except:
                        self.AddWarning(u'MXD with path {0} cannot be saved'.format(mxd))
                        tb = sys.exc_info()
                        self.AddWarning("Line %i" % tb[2].tb_lineno)
                        self.AddWarning(traceback.format_exc())
                except:
                    self.AddWarning(u'MXD sources with path {0} cannot be replaced'.format(mxd))
                    tb = sys.exc_info()
                    self.AddWarning("Line %i" % tb[2].tb_lineno)
                    self.AddWarning(traceback.format_exc())
            except:
                self.AddWarning(u'MXD with path {0} cannot be opened'.format(mxd))
                tb = sys.exc_info()
                self.AddWarning("Line %i" % tb[2].tb_lineno)
                self.AddWarning(traceback.format_exc())

    def AddRealatedTablesToMXD(self, MXD, silent=False):
        """
            Procedure adds all mising related tables to MXD
            Args:
                self: The reserved object 'self'
                mxd: path to MXD,
                silent: does the messages will be supressed
        """
        
        self.GDBTools = GDBHelper.GDBHelper(self.gp)
        T = TimerHelper.TimerHelper()
        if not silent == True:
            self.AddMessage(u'    Processing document [{0}]'.format(MXD))
        if not self.gp.Exists(MXD):
            if not silent == True:
                self.AddWarning(u'MXD with path {0} has not been found'.format(MXD))
        else:
            if not silent == True:
                 self.AddMessage(u'        Document found')
            T.TimerReset()
            try:
                Doc = self.gp.mapping.MapDocument(MXD)
                if not silent == True: 
                    self.AddMessage(u'        Document opened - {0}'.format(T.GetTimeReset()))
                try:
                    Relations = list()
                    for lyr in self.gp.mapping.ListLayers(Doc):
                        self.__ProcessLyr(lyr,'            ', Relations, silent = silent)
                    Relations = set(Relations)

                    if not silent == True: 
                        self.AddMessage('\n           ' + u'Found tables:')
                        for tabl in Relations:
                            self.AddMessage('              > ' + tabl)

                    remList = list()
                    for tab in self.gp.mapping.ListTableViews(Doc):
                        for rel in Relations:
                            if tab.datasetName.lower() == rel.lower().split('\\')[-1]:
                                remList.append(rel)
                    Relations = [x for x in Relations if x not in remList]

                    if not silent == True: 
                        self.AddMessage('\n           ' + u'Tables missing from MXD:')
                        for tabl in Relations:
                            self.AddMessage('              > ' + tabl)
                    
                    for rel in Relations:
                        addTable = self.gp.mapping.TableView(rel)
                        self.gp.mapping.AddTableView(Doc.activeDataFrame, addTable)

                    if not silent == True: 
                        self.AddMessage(u'\n        Document tables processed - {0}'.format(T.GetTimeReset()))
                    try:
                        Doc.save()
                        del Doc
                        if not silent == True: 
                            self.AddMessage(u'        Document saved - {0}'.format(T.GetTimeReset()))
                    except:
                        self.AddWarning(u'MXD with path {0} cannot be saved'.format(MXD))
                        tb = sys.exc_info()
                        self.AddWarning("Line %i" % tb[2].tb_lineno)
                        self.AddWarning(traceback.format_exc())
                except:
                    self.AddWarning(u'MXD sources with path {0} cannot be processed'.format(MXD))
                    tb = sys.exc_info()
                    self.AddWarning("Line %i" % tb[2].tb_lineno)
                    self.AddWarning(traceback.format_exc())
            except:
                self.AddWarning(u'MXD with path {0} cannot be opened'.format(MXD))
                tb = sys.exc_info()
                self.AddWarning("Line %i" % tb[2].tb_lineno)
                self.AddWarning(traceback.format_exc())

    def __ProcessLyr(self, lyr, step, Tables, silent=False):
        if lyr.isFeatureLayer == True:
            if not silent == True: 
                self.AddMessage(step + lyr.name)
            Relations = list()
            self.GDBTools.GetRelations(lyr.workspacePath, self.gp.Describe(lyr.dataSource), Relations)
            for rel in Relations:
                DRel = self.gp.Describe(os.path.join(lyr.workspacePath, rel))
                if DRel.dataElementType == u'DETable':
                    Tables.append(os.path.join(lyr.workspacePath, rel).lower())
                    if not silent == True: 
                        self.AddMessage(step + '    ' + lyr.name + " -> " + rel)
        if lyr.isGroupLayer == True:
            if not silent == True: 
                self.AddMessage(step + lyr.name + ':')
            for sublyr in self.gp.mapping.ListLayers(lyr):
                if not silent == True: 
                    self.__ProcessLyr(sublyr, step + '    ', Tables)