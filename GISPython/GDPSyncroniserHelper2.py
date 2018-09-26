# -*- coding: utf-8 -*-
"""
     Data synchronization module 2 (synchronizes data between tables)

     Second version is ment for advanced scenarious, but opereates data inMemory so it,s not intended for large data sets.
"""
import TimerHelper

class GDPSyncroniserHelper2(object):
    """ESRI table synchronization class 2

       Second version is ment for advanced scenarious, but opereates data inMemory so it,s not intended for large data sets
    """

    def __init__(self, gp, Tool=None):
        """Class initialization operation

        Args:
            self: The reserved object 'self'
            gp: ArcPy GP object
        """
        self.gp = gp
        if Tool != None:
            self.isTool = True
        else:
            self.isTool = False
        self.Tool = Tool

    def AddWarning(self, str):
        """Wrapper for the 'AddWarning' procedure

        Args:
            self: The reserved object 'self'
            str: Output string
        """
        if self.isTool:
            self.Tool.AddWarning(str)
        else:
            self.gp.AddWarning(str)

    def AddMessage(self, str):
        """Wrapper for the 'AddMessage' procedure

        Args:
            self: The reserved object 'self'
            str: Output string
        """
        if self.isTool:
            self.Tool.AddMessage(str)
        else:
            self.gp.AddMessage(str)

    def DoSync(self, definition, workspace=None, startEditing=False, startOperation=False, with_undo=False, multiuser=False):
        """Data synchronization procedure

        Args:
            self: The reserved object 'self'
            definition: 'SyncDefinition' object which describes the synchronization parameters
            workspace: DB in which to start data editing
            startEditing: Start the edit session in the DB specified in 'workspace' parameter? (Default = False)
            startOperation: Start the edit operation in the DB specified in 'workspace' parameter? (Default = False)
            with_undo: Sets whether the undo and redo stacks are enabled or disabled for an edit session. (Default = False)
            multiuser: Sets whether a DB contains a nonversioned, or versioned dataset. (Default = False)

        Returns:
            * output - list of dictionary items containig:
                - id: record id, 
                - syncResult: notInitialized,  synchronized, inserted, error
                - error: error mesage or '',
                - updated: true if inserted or updated
        """

        # move parameters to self
        self.definition = definition
        self.workspace = workspace
        self.startEditing = startEditing
        self.startOperation = startOperation
        self.with_undo = with_undo
        self.multiuser = multiuser

        # set up fields parameters
        self.definition.inTableFields = (self.definition.inTableJoinField,) + self.definition.inTableFields
        self.definition.outTableFields = (self.definition.outTableJoinField,) + self.definition.outTableFields

        # Ouput Sync process description
        self.AddMessage(u'>>>>Start the synchronization of the tables {0} and {1}'.format(self.definition.inTable, self.definition.outTable))
        self.AddMessage(u'>>>>Synchronization mode is "{0}"'.format(self.definition.mode))
        self.AddMessage(u'>>>>>>>>Join {0}.{1}={2}.{3}'.format(self.definition.inTable, self.definition.inTableJoinField, self.definition.outTable, self.definition.outTableJoinField))
        self.AddMessage(u'>>>>>>>>Input fields: [{0}]'.format(", ".join(self.definition.inTableFields)))
        if self.definition.HasInTableQuery():
            self.AddMessage(u'>>>>>>>>Input query: [{0}]'.format(self.definition.inTableQuery))
        self.AddMessage(u'>>>>>>>>Output fields: [{0}]'.format(", ".join(self.definition.outTableFields)))
        if self.definition.HasOutTableQuery():
            self.AddMessage(u'>>>>>>>>Output query: [{0}]'.format(self.definition.outTableQuery))
        if self.definition.SourceToDestination():
            self.AddMessage(u'>>>>>>>>Do create new records: [{0}]'.format(self.definition.createNew))
        if self.definition.SourceToDestination():
            self.AddMessage(u'>>>>>>>>Do allow one to many join records: [{0}]'.format(self.definition.allowMultiple))

        # organize editor start
        if startEditing or startOperation:
            self.edit = self.gp.da.Editor(workspace)
        if startEditing:
            self.edit.startEditing(with_undo, multiuser)
        if startOperation:
            self.edit.startOperation()

        output = None

        # Sync process
        if self.definition.SourceToDestination():
            output = self.__SyncSourceToDestination()
        else:
            output = self.__SyncDestinationToSource()

        # organize editor stop
        if startOperation:
            self.edit.stopOperation()
        if startEditing:
            self.edit.stopEditing(True)

        # end
        return output

    def __SyncSourceToDestination(self):
        """Procedure performs syncronization of type Source To Destination

        Args:
            self: The reserved object 'self'
       
        Returns:
            * output - list of dictionary items containig:
                - id: record id, 
                - syncResult: notInitialized,  synchronized, inserted, error
                - error: error mesage or '',
                - updated: true if inserted or updated
        """
        # get summary record count
        recordCount = 0
        with self.gp.da.SearchCursor(self.definition.inTable, self.definition.inTableFields, self.definition.inTableQuery) as cur:
             for row in cur:
                recordCount = recordCount + 1
        self.AddMessage(u'>>>> ...Records to process {0}'.format(recordCount))

        rezultList =[]

        updatedCount = 0
        processedCount = 0
        processedCountOperation = 0
        errCount = 0

        with self.gp.da.SearchCursor(self.definition.inTable, self.definition.inTableFields, self.definition.inTableQuery) as inCur:
            T = TimerHelper.TimerHelper()
            for inRow in inCur:
                syncItem = SyncItem2()
                syncItem.inSyncRow = inRow
                syncItem.id = inRow[0]

                with self.gp.da.UpdateCursor(self.definition.outTable, self.definition.outTableFields, u'{0} = {2}{1}{2}'.format(self.definition.outTableJoinField, syncItem.id, self.definition.idvalueseparator)) as outCur:
                    recordsFoundCount = 0
                    for outRow in outCur:
                        #print "rec {0} - {1}".format(u'{0} = {2}{1}{2}'.format(self.definition.outTableJoinField, syncItem.id, self.definition.idvalueseparator), (recordsFoundCount == 0 or self.definition.allowMultiple)) 
                        if recordsFoundCount == 0 or self.definition.allowMultiple:
                            recordsFoundCount = recordsFoundCount + 1
                            if recordsFoundCount>1:
                                syncItem = SyncItem2()
                                syncItem.inSyncRow = inRow
                                syncItem.id = inRow[0]
                            syncItem.outSyncRow = outRow
                            syncItem.DoSyncFields()
                            if syncItem.updated:
                                outCur.updateRow(syncItem.outSyncRow)
                                updatedCount = updatedCount + 1
                                syncItem.ClerRowInfo()
                                syncItem.syncResult = 'synchronized'
                                rezultList.append(syncItem.GetRowStatussInfo())
                        else:
                            syncItem = SyncItem2()
                            syncItem.inSyncRow = inRow
                            syncItem.id = inRow[0]
                            errCount = errCount + 1
                            syncItem.error =  u"Error: row in the results table is not unique " + self.definition.messageDefinition.format(*syncItem.inSyncRow)
                            self.AddMessage(u'        ...{0}'.format(syncItem.error))
                            syncItem.ClerRowInfo()
                            syncItem.syncResult = 'error'
                            rezultList.append(syncItem.GetRowStatussInfo())

                if recordsFoundCount == 0 and self.definition.createNew:
                        with self.gp.da.InsertCursor(self.definition.outTable, self.definition.outTableFields) as insCur:
                            newRow = [None for _ in range(len(syncItem.inSyncRow))]
                            syncItem.outSyncRow = newRow
                            syncItem.DoSyncFields()
                            if syncItem.updated:
                                insCur.insertRow(syncItem.outSyncRow)
                                updatedCount = updatedCount + 1
                                syncItem.ClerRowInfo()
                                syncItem.syncResult = 'inserted'
                                rezultList.append(syncItem.GetRowStatussInfo())
                if recordsFoundCount == 0 and not self.definition.createNew:
                    errCount = errCount + 1
                    syncItem.error =  u"Error: no related records found in the results table " + self.definition.messageDefinition.format(*syncItem.inSyncRow)
                    self.AddMessage(u'        ...{0}'.format(syncItem.error))
                    syncItem.id = inRow[0]
                    syncItem.ClerRowInfo()
                    syncItem.syncResult = 'error'
                    rezultList.append(syncItem.GetRowStatussInfo())

                processedCount = processedCount + 1
                processedCountOperation = processedCountOperation + 1

                if processedCountOperation >= 1000:
                    if self.isTool:
                        self.AddMessage(u'>>>> ...Processed [{0}] from [{1}], stored [{2}], faulty [{3}] ({4})'.format(processedCount, recordCount, updatedCount, errCount, T.GetTimeReset()))
                    processedCountOperation = 0
                    if self.startOperation:
                        self.edit.stopOperation()
                    if self.startOperation:
                        self.edit.startOperation()

        self.AddMessage(u'>>>> ...Processed [{0}], stored [{1}], faulty [{2}]'.format(processedCount, updatedCount, errCount))
        return rezultList

    def __SyncDestinationToSource(self):
        """Procedure performs syncronization of type Destination To Source

        Args:
            self: The reserved object 'self'
       
        Returns:
            * output - list of dictionary items containig:
                - id: record id, 
                - syncResult: notInitialized,  synchronized, inserted, error
                - error: error mesage or '',
                - updated: true if inserted or updated
        """
        # get summary record count
        recordCount = 0
        with self.gp.da.SearchCursor(self.definition.outTable, self.definition.outTableFields, self.definition.outTableQuery) as cur:
             for row in cur:
                recordCount = recordCount + 1
        self.AddMessage(u'>>>> ...Records to process {0}'.format(recordCount))

        rezultList =[]

        updatedCount = 0
        processedCount = 0
        processedCountOperation = 0
        errCount = 0
        
        with self.gp.da.UpdateCursor(self.definition.outTable, self.definition.outTableFields, self.definition.outTableQuery) as outCur:
            T = TimerHelper.TimerHelper()
            for outRow in outCur:
                syncItem = SyncItem2()
                syncItem.outSyncRow = outRow
                syncItem.id = outRow[0]

                with self.gp.da.SearchCursor(self.definition.inTable, self.definition.inTableFields, u'{0} = {2}{1}{2}'.format(self.definition.inTableJoinField, syncItem.id, self.definition.idvalueseparator)) as inCur:
                    recordsFoundCount = 0
                    for inRow in inCur:
                        #print "rec {0} - {1}".format(u'{0} = {2}{1}{2}'.format(self.definition.outTableJoinField, syncItem.id, self.definition.idvalueseparator), (recordsFoundCount == 0 or self.definition.allowMultiple)) 
                        if recordsFoundCount == 0:
                            recordsFoundCount = recordsFoundCount + 1
                            syncItem.inSyncRow = inRow
                            syncItem.DoSyncFields()
                            if syncItem.updated:
                                outCur.updateRow(syncItem.outSyncRow)
                                updatedCount = updatedCount + 1
                                syncItem.ClerRowInfo()
                                syncItem.syncResult = 'synchronized'
                                rezultList.append(syncItem.GetRowStatussInfo())
                        else:
                            syncItem = SyncItem2()
                            syncItem.outSyncRow = outRow
                            syncItem.id = outRow[0]
                            errCount = errCount + 1
                            syncItem.error =  u"Error: row in the source table is not unique " + self.definition.messageDefinition.format(*syncItem.outSyncRow)
                            self.AddMessage(u'        ...{0}'.format(syncItem.error))
                            syncItem.ClerRowInfo()
                            syncItem.syncResult = 'error'
                            rezultList.append(syncItem.GetRowStatussInfo())

                if recordsFoundCount == 0:
                    errCount = errCount + 1
                    syncItem.error =  u"Error: no related records found in the source table " + self.definition.messageDefinition.format(*syncItem.outSyncRow)
                    self.AddMessage(u'        ...{0}'.format(syncItem.error))
                    syncItem.ClerRowInfo()
                    syncItem.syncResult = 'error'
                    rezultList.append(syncItem.GetRowStatussInfo())

                processedCount = processedCount + 1
                processedCountOperation = processedCountOperation + 1

                if processedCountOperation >= 1000:
                    if self.isTool:
                        self.AddMessage(u'>>>> ...Processed [{0}] from [{1}], stored [{2}], faulty [{3}] ({4})'.format(processedCount, recordCount, updatedCount, errCount, T.GetTimeReset()))
                    processedCountOperation = 0
                    if self.startOperation:
                        self.edit.stopOperation()
                    if self.startOperation:
                        self.edit.startOperation()

        self.AddMessage(u'>>>> ...Processed [{0}], stored [{1}], faulty [{2}]'.format(processedCount, updatedCount, errCount))
        return rezultList


class SyncItem2(object):
    """class for storing sysnc data item"""

    def __init__(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """
        self.inSyncRow = () # in sync row
        self.outSyncRow = () # out sync row
        self.syncResult = 'notInitialized' # sync state notInitialized, error, ok
        self.error = '' # sync error message
        self.id = '' # sync id
        self.updated = False # if row had changes and needed to be saved then True

    def ClerRowInfo(self):
        """Clears savec row objects"""
        del self.inSyncRow
        del self.outSyncRow

    def GetRowStatussInfo(self):
        """Gets Dict of row statuss reprezenting objects"""
        return {
                "id": self.id, 
                "syncResult": self.syncResult, 
                "error": self.error,
                "updated": self.updated
                }

    def DoSyncFields(self):
        """Procedure performs the field synchronization

        Args:
            self: The reserved object 'self'
            inRow: Row to synchronize
            outRow: Row to which synchronize

        Returns:
            * output - 0, If no changes were necessary; 1, If there were any changes
            * outRow - Altered row
        """
        inRow = self.inSyncRow
        outRow = self.outSyncRow
        for x in range(0, len(inRow)):
            if inRow[x] != outRow[x]:
                outRow[x] = inRow[x]
                self.updated = True
        self.outSyncRow = outRow


class SyncDefinition2(object):
    """Synchronization definition description class"""

    def __init__(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """
        self.inTable = "" # input Tale
        self.inTableFields = () # tuple of input table fields
        self.inTableQuery = None # query for input table
        self.inTableJoinField = "" # Field for input table to be used in relation
        self.outTable = "" # destination table
        self.outTableFields = () # tuple of output table fields
        self.outTableQuery = None # query for output table (used only in Destination To Source Sync mode)
        self.outTableJoinField = "" # Field for ouput table to be used in relation
        self.messageDefinition = "" # Output message formatting
        self.idvalueseparator = "" # "'"for Text fields
        self.createNew = False # whether to create new record if input row match has not been found (used only in Source To Destination Sync mode)
        self.allowMultiple = False # whhether it is okay to sync more than one source roe to multiple rows in destination (used only in Source To Destination Sync mode)
        self.mode = "Source To Destination" # Source To Destination or Destination To Source. Sync mode that specifies sync row search type. Sync rows found in destination then search for coresponding rows in source (Destination To Source) or find all rows in source and sync with coresponding rows in destination (Source To Destination).

    def HasInTableQuery(self):
        """Returns whether input table has query"""
        hasInQuery = False
            
        if self.inTableQuery != None:
            hasInQuery = True

        return hasInQuery

    def HasOutTableQuery(self):
        """Returns whether input table has query"""
        hasInQuery = False
            
        if self.outTableQuery != None:
            hasInQuery = True

        return hasInQuery

    def SourceToDestination(self):
        """Returns whether sync mode is Source To Destination"""
        isStoD = False
            
        if self.mode.upper() == "Source To Destination".upper():
            isStoD = True

        return isStoD