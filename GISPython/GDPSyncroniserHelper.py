# -*- coding: utf-8 -*-
"""
     Data synchronization module (synchronizes data between tables)
"""

class GDPSyncroniserHelper(object):
    """ESRI table synchronization class"""

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
            * output - Returns the report about the process execution
            * outputErrors - Returns the error description
        """
        outputErrors = u""
        output = u""

        if definition.inTableQuery != None:
            hasInQuery = True
        else:
            hasInQuery = False

        inFields = ()
        inFields = (definition.inTableJoinField, ) + definition.inTableFields
        outFields = ()
        outFields = (definition.outTableJoinField, ) + definition.outTableFields

        self.AddMessage(u'>>>>Start the synchronization of the tables {0} and {1}'.format(definition.inTable, definition.outTable))
        self.AddMessage(u'>>>>>>>>Join {0}.{1}={2}.{3}'.format(definition.inTable, definition.inTableJoinField, definition.outTable, definition.outTableJoinField))
        self.AddMessage(u'>>>>>>>>Input fields: [{0}]'.format(", ".join(definition.inTableFields)))
        if hasInQuery:
            self.AddMessage(u'>>>>>>>>Input query: [{0}]'.format(definition.inTableQuery))
        self.AddMessage(u'>>>>>>>>Output fields: [{0}]'.format(", ".join(definition.outTableFields)))

        if startEditing or startOperation:
            edit = self.gp.da.Editor(workspace)
        if startEditing:
            edit.startEditing(with_undo, multiuser)
        if startOperation:
            edit.startOperation()

        with self.gp.da.SearchCursor(definition.inTable, inFields, definition.inTableQuery) as cur:
            i = 0
            j = 0
            k = 0
            err = 0
            for row in cur:
                output = self.__DoSyncRow(row, definition.outTable, outFields, definition.outTableJoinField, definition.messageDefinition, definition.idvalueseparator, definition.createNew)
                if type(output) is int:
                    i = i + output
                else:
                    if self.isTool:
                        self.AddMessage(u'        ...{0}'.format(output))
                        outputErrors = outputErrors + u'{0}\n'.format(output)
                        err = err + 1
                j = j + 1
                k = k + 1

                if k >= 1000:
                    if self.isTool:
                        self.AddMessage(u'>>>> ...Processed [{0}], stored [{1}], faulty [{2}]'.format(j, i, err))
                    k = 0
                    if startOperation:
                        edit.stopOperation()
                    if startOperation:
                        edit.startOperation()

        if startOperation:
            edit.stopOperation()
        if startEditing:
            edit.stopEditing(True)

        if self.isTool:
            self.AddMessage(u'>>>> ...Processed [{0}], stored [{1}], faulty [{2}]'.format(j, i, err))
            output = u'Processed [{0}], stored [{1}], faulty [{2}]'.format(j, i, err)

        return output, outputErrors

    def __DoSyncRow(self, inRow, outTable, outTableFields, outTableJoinField, messageString, idvalueseparator, createNew):
        """Procedure performs row synchronization

        Args:
            self: The reserved object 'self'
            inRow: Row to synchronize
            outTable: Output table
            outTableFields: Output table fields
            outTableJoinField: Output table join field
            messageString: Output message formatting
            createNew: Create new record if needed

        Returns:
            * output - 0, If no changes were necessary; 1, If there were any changes
            * Error description (in case there were errors)
        """
        if inRow[0] == None:
            return u"Error: join field is empty " + messageString.format(*inRow)

        with self.gp.da.UpdateCursor(outTable, outTableFields, '{0} = {2}{1}{2}'.format(outTableJoinField, inRow[0], idvalueseparator)) as cur:
            output = 0
            i = 0
            foundRow = False
            for row in cur:
                if i == 0:
                    foundRow = True
                    output, row = self.__DoSyncFields(inRow, row)
                    if output == 1:
                        cur.updateRow(row)
                    i = i+1
                else:
                    return u"Error: row in the results table is not unique" + messageString.format(*inRow)

            if not foundRow:
                if createNew:
                    with self.gp.da.InsertCursor(outTable, outTableFields) as insCur:
                        newRow = [None for _ in range(len(inRow))]
                        output, newRow = self.__DoSyncFields(inRow, newRow)
                        insCur.insertRow(newRow)
                else:
                    return u"Error: no related records found in the results table " + messageString.format(*inRow)

            return output

    def __DoSyncFields(self, inRow, outRow):
        """Procedure performs the field synchronization

        Args:
            self: The reserved object 'self'
            inRow: Row to synchronize
            outRow: Row to which synchronize

        Returns:
            * output - 0, If no changes were necessary; 1, If there were any changes
            * outRow - Altered row
        """
        output = 0
        for x in range(0, len(inRow)):
            if inRow[x] != outRow[x]:
                outRow[x] = inRow[x]
                output = 1
        return output, outRow

class SyncDefinition(object):
    """Synchronization definition description class"""

    def __init__(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """
        self.inTable = ""
        self.inTableFields = ()
        self.inTableQuery = None
        self.inTableJoinField = ""
        self.outTable = ""
        self.outTableFields = ()
        self.outTableJoinField = ""
        self.messageDefinition = ""
        self.idvalueseparator = ""
        self.createNew = False
