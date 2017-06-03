# -*- coding: utf-8 -*-
"""
     GDB operations module
"""
import os
import uuid

class GDBHelper:
    """Class for easing the ESRI geodatabase operations"""

    def __init__(self, gp, Tool=None):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            gp: ArcPy GP object
        """
        self.gp = gp
        if not Tool == None:
            self.isTool = True
        else:
            self.isTool = False
        self.Tool = Tool

    def AddWarning(self, str):
        if self.isTool:
            self.Tool.AddWarning(str)
        else:
            self.gp.AddWarning(str)

    def OutputMessages(self):
        if self.isTool:
            self.Tool.OutputMessages(str)


    def GetDSConnectedElements(self, ConnDBSchema, DBName, IncludeMe=False):
        """Function defines all the tables which are linked with the FeatureDataset

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to DB schema
            DBName: DB name to process
            IncludeMe: Optional. Default = False. Indicates if DB classes will be returned in the returned list

        Returns:
            * Result list with the found object classes
        """
        self.gp.env.workspace = ConnDBSchema + '\\' + DBName
        fcs = self.gp.ListFeatureClasses()
        DSfcs = fcs
        ResultList = list()
        if DSfcs != None:
            for fc in fcs:
                self.gp.AddMessage(u'            ... searching relations ' + fc)
                dfc = self.gp.Describe(fc)
                ResultList = list(set(self.GetRelations(ConnDBSchema, dfc, ResultList) + ResultList))
            for x in DSfcs:
                if x in ResultList:
                    ResultList.remove(x)
            if IncludeMe == True:
                DSfcs2 = list()
                for x in DSfcs:
                    DSfcs2.append(DBName + '\\' + x)
                ResultList = list(set(ResultList + DSfcs2))
        return ResultList

    def GetRelations(self, ConnDBSchema, dfc, existingObjects):
        """Auxiliary function for 'GetDSConnectedElements' function

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to the DB schema
            dfc: Describe 'FeatureClass' object
            existingObjects: List of existing objects

        Returns:
            List of the found objects
        """
        existingObjects.append(dfc.name)
        rcs = dfc.relationshipClassNames
        ResultList = list()
        for rc in rcs:
            drc = self.gp.Describe(ConnDBSchema + '\\' + rc)
            if drc.dataType == "RelationshipClass":
                origins = drc.originClassNames
                destinations = drc.destinationClassNames
                ResultList = list(set(ResultList + origins))
                ResultList = list(set(ResultList + destinations))
            else:
                self.gp.AddWarning(u'        ...Descriptive object for relational class [' + ConnDBSchema + '\\' + rc + u'] not found')
        for x in existingObjects:
            if x in ResultList:
                ResultList.remove(x)
        for x in ResultList:
            dfc2 = self.gp.Describe(ConnDBSchema + '\\' + x)
            existingObjects = list(set(existingObjects + self.GetRelations(ConnDBSchema, dfc2, existingObjects)))
        return existingObjects

    def CalculateXY(self, Layer, Field, type, Query):
        """Function for calculating the fields X and Y

        Args:
            self: The reserved object 'self'
            Layer:  Input layer
            Field: The field to be calculated
            type: X or Y
            Query: Layer query
        """
        xExpression = "getcord('X', !SHAPE.CENTROID!)"
        yExpression = "getcord('Y', !SHAPE.CENTROID!)"
        codeBlock = "def getcord(typ, Cent=''):\\n    Cent = Cent.replace('\\\"', '')\\n    if typ == 'X':\\n        if not Cent == '':\\n            return float(Cent.split()[0])\\n        else:\\n            return 0\\n    else:\\n        if not Cent == '':\\n            return float(Cent.split()[1])\\n        else:\\n            return 0\\n"

        CalcLayer = (self.gp.MakeTableView_management(Layer, "#" + Field, Query, "#")).getOutput(0)
        if type == 'X':
            self.gp.CalculateField_management(CalcLayer, Field, xExpression, "PYTHON", codeBlock)
        else:
            self.gp.CalculateField_management(CalcLayer, Field, yExpression, "PYTHON", codeBlock)

    def HasField(self, ConnDBSchema, Table, Field):
        """Function determines if field already exists in the table

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to the DB schema
            Table: Table
            Field: The field to be calculated
        """
        self.gp.env.workspace = ConnDBSchema
        dt = self.gp.Describe(Table)
        fs = dt.fields
        for f in fs:
            if f.name.upper() == Field.upper():
                return True
        return False

    def DelleteField(self, ConnDBSchema, TABLENAME, FIELDNAME):
        """Function eases work with the ESRI field deletion function DeleteField_management

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to the DB schema
            Table: Table
            Field: The field to be calculated
        """
        if self.HasField(ConnDBSchema, TABLENAME, FIELDNAME):
            try:
                self.gp.DeleteField_management(os.path.join(ConnDBSchema, TABLENAME), FIELDNAME)
            except:
                self.AddWarning(u'      ...Failed to delete the field [{0}.{1}]'.format(TABLENAME, FIELDNAME))
            self.OutputMessages()
        else:
            self.AddWarning(u'      ...Cannot delete the field [{0}.{1}] which does not exist'.format(TABLENAME, FIELDNAME))

    def CreateIndex(self, ConnDBSchema, TABLENAME, FIELDNAME):
        """Function eases work with the ESRI indexing function 'AddIndex_management'

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to the DB schema
            Table: The table
            Field: The field to be calculated
        """
        idxName = 'idx' + TABLENAME.split('.')[1][:5] + FIELDNAME[:10]
        if self.HasField(ConnDBSchema, TABLENAME, FIELDNAME):
            try:
                self.gp.AddIndex_management(os.path.join(ConnDBSchema, TABLENAME), FIELDNAME, idxName)
            except:
                self.AddWarning(u'Failed to create index [{2}] field [{0}.{1}]'.format(TABLENAME, FIELDNAME, idxName))
            self.OutputMessages()
        else:
            self.AddWarning(u'      ...Cannot create the index [{2}] for the field [{0}.{1}] because the field does not exist'.format(TABLENAME, FIELDNAME, idxName))


    def DelleteObject(self, ConnDBSchema, ObjectName, ObjectType='#'):
        """Function eases work with the ESRI object deletion function 'Delete_management'

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to the DB schema
            ObjectName: Object to be deleted
            ObjectType: Field to be deleted
        """
        try:
            self.gp.Delete_management(os.path.join(ConnDBSchema, ObjectName), ObjectType)
        except:
            self.AddWarning(u'Failed to delete the object [' +  ObjectName + ']')
        self.OutputMessages()

    def DelleteDomain(self, ConnDBSchema, ObjectName):
        """Function eases work with the ESRI domain deletion function 'DeleteDomain_management'

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to the DB schema
            ObjectName: The domain to be deleted
        """
        try:
            self.gp.DeleteDomain_management(ConnDBSchema, ObjectName)
        except:
            self.AddWarning(u'Failed to delete the domain [' +  ObjectName + ']')
        self.OutputMessages()

    def ClearData(self, ConnDBSchema, ObjectName, ObjectType="TABLE"):
        """Function eases feature deletion from layers and tables

        Args:
            self: The reserved object 'self'
            ConnDBSchema: Connection to the DB schema
            ObjectName: The table or layer containing features to be deleted
            ObjectType: Type: "TABLE" or "FC"
        """
        try:
            if ObjectType == 'TABLE':
                self.gp.DeleteRows_management(os.path.join(ConnDBSchema, ObjectName))
            else:
                self.gp.DeleteFeatures_management(os.path.join(ConnDBSchema, ObjectName))
        except:
            self.AddWarning(u'Failed to delete data from [' +  ObjectName + ']')
        self.OutputMessages()

    def Decode(self, val, DecodeDict):
        """Function decodes one value to another

        Args:
            self: The reserved object 'self'
            val: Value to be decoded
            DecodeDict: Python Dictionary syntax which describes the decoding process - for example {'Key1':'Val1','Key2':'Val2'}
        """
        Options = DecodeDict
        if val in Options:
            return Options[val]
        else:
            return val

    def DecodeField(self, Layer, Field, DecodeField, DecodeDict, Query=None, workspace=None, startEditing=False, startOperation=False, with_undo=False, multiuser=False):
        """Function does field value recalculation decoding values from one to another. Used, for example, in clasificator value recalculation.

        Args:
            self: The reserved object 'self'
            Layer: Layer in which to decode
            Field: Field in which to decode
            DecodeField: Field from which to decode
            DecodeDict: Python Dictionary syntax which describes the decoding process - for example {'Key1':'Val1','Key2':'Val2'}
            Query: Layer query
            workspace: DB in which to start data editing
            startEditing: Start the edit session in the DB specified in the 'workspace' parameter
            startEditing: Start the edit operation in the DB specified in the 'workspace' parameter
            with_undo: Sets whether the undo and redo stacks are enabled or disabled for an edit session.
            multiuser: When False, you have full control of editing a nonversioned, or versioned dataset.
        """
        if self.isTool:
            self.Tool.AddMessage(u'>>>>Executing the layer ' + uni(Layer) + u' field ' + uni(Field) + u' decoding ' + uni(DecodeDict) + u' after field ' + uni(DecodeField) + u' records after query ' + uni(Query) + ' - ' + self.Tool.MyNow())

        if startEditing or startOperation:
            edit = self.gp.da.Editor(workspace)
        if startEditing:
            edit.startEditing(with_undo, multiuser)
        if startOperation:
            edit.startOperation()

        if Field != DecodeField:
            with self.gp.da.UpdateCursor(Layer, [Field, DecodeField], Query) as cur:
                i = 0
                for row in cur:
                    row[0] = self.Decode(row[1], DecodeDict)
                    cur.updateRow(row)
                    i += 1
        else:
            with self.gp.da.UpdateCursor(Layer, [Field], Query) as cur:
                i = 0
                for row in cur:
                    row[0] = self.Decode(row[0], DecodeDict)
                    cur.updateRow(row)
                    i += 1

        if startOperation:
            edit.stopOperation()
        if startEditing:
            edit.stopEditing(True)

        if self.isTool:
            self.Tool.AddMessage(u'>>>> ...Processed  ' + str(i) + u' rows')


class RowHelper:
    """Row processing class"""

    def __init__(self, gp, Tool=None):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            gp: ArcPy GP object
        """
        self.gp = gp
        if not Tool == None:
            self.isTool = True
        else:
            self.isTool = False
        self.Tool = Tool

    def GetUniqueValues(self, festureClass, getField, where_clause=None):
        """Get unique values from the field in the table (Only in DB)

        Args:
            self: The reserved object 'self'
            festureClass: The feature class containing the rows to be searched
            getField: The field from which to retrieve unique values
            where_clause: SQL WHERE clause to obtain the data
        """
        rezultList = list()
        with self.gp.da.SearchCursor(festureClass, field_names=(getField), where_clause=where_clause, sql_clause=('Distinct', None)) as cursor:
            for row in cursor:
                rezultList.append(row[0])
        return rezultList

    def ValidateRowsForSQLClause(self, festureClass, fields, where_clause, outStringformat):
        """Validate the rows with the SQL clause

        Args:
            self: The reserved object 'self'
            festureClass: The feature class containing the rows to be searched
            fields: A list of the field names (order is important, because the parameter 'outStringformat' is configured by this parameter)
            where_clause: SQL WHERE clause to obtain the data
            outStringformat: Error output text on the found error.
                                You can use the 'unicode.format' function notation {#} to transfer the row values.
                                For example - a field with the index 0 in the list of fields with 'outStringformat' parameter value: u"faulty feature OID: {0}" will return the string: u"faulty feature OID: 123", where 123 is the 'objectid' field value for found record.
        """
        rezultList = []
        with self.gp.da.SearchCursor(festureClass, field_names=fields, where_clause=where_clause) as cursor:
            for row in cursor:
                rezultList.append(outStringformat.format(*row))
        return rezultList

    def ValidateRowsForFieldValueList(self, festureClass, getField, fields, valuelist, where_clause, outStringformat):
        """Check rows if the field matches the unique value list

        Args:
            self: The reserved object 'self'
            festureClass: The feature class containing the rows to be searched
            getField: Field to check
            fields: A list of field names (order is important, because parameter 'outStringformat' is configured by this parameter !!! 'getField' value should be in this list!!!
            valuelist: A list of values
            where_clause: SQL WHERE clause to obtain the data
            outStringformat: Error output text on the found error.
                                You can use the 'unicode.format' function notation {#} to transfer the row values.
                                For example - a field with the index 0 in the list of fields with 'outStringformat' parameter value: u"faulty feature OID: {0}" will return the string: u"faulty feature OID: 123", where 123 is the 'objectid' field value for found record.
        """
        rezultList = []
        with self.gp.da.SearchCursor(festureClass, field_names=fields, where_clause=where_clause) as cursor:
            for row in cursor:
                if not row[fields.index(getField)] in valuelist:
                    rezultList.append(outStringformat.format(*row))
        return rezultList

class SimpleAppend:
    """Class for easing the operations with the 'Append' function"""
    def __init__(self, _Tool, _InWSp, _OutWSp):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            self.InWS: Input workspace
            self.OutWSp: Output workspace
        """
        self.Tool = _Tool
        self.InWSp = _InWSp
        self.OutWSp = _OutWSp

    def Append(self, inName, OutName):
        """Function for 'Append' operation automation

        Args:
            self: The reserved object 'self'
            inName: Input object name
            OutName:  Output object name
        """
        inLayer = os.path.join(self.InWSp, inName)
        outLayer = os.path.join(self.OutWSp, OutName)
        self.Tool.AddMessage("")
        self.Tool.AddMessage("-----------" + OutName + "------------" + self.Tool.MyNow())
        self.Tool.gp.DeleteRows_management(outLayer)
        self.Tool.OutputMessages()
        self.Tool.gp.Append_management(inLayer, outLayer, "NO_TEST", "#", "#")
        self.Tool.OutputMessages()
        try:
            self.Tool.gp.Analyze_management(outLayer, "BUSINESS")
            self.Tool.OutputMessages()
        except:
            self.Tool.AddMessage(u"Warning - could not carry out the 'Analyze' operation!")

def uni(value):
    if value == None:
        return ''
    try:
        return unicode(value)
    except:
        return value.decode('cp1257')
