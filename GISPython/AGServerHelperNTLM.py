# -*- coding: utf-8 -*-
"""
     Module for operations with ArcGIS Server services
"""

# For system tools
import sys

# For Http calls
import httplib, urllib, json, urllib2
from ntlm import HTTPNtlmAuthHandler
import MyError

class AGServerHelperNTLM(object):

    def __init__(self, username, password, ags_admin_url, tool=None):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            username: ArcGIS Server administrator username
            password: ArcGIS Server administrator password
            ags_admin_url: ArcGIS server rest admin url
            Tool: GISPython tool (optional)
        """
        self.username = username
        self.password = password
        self.ags_admin_url = ags_admin_url
        self.serverurl = ags_admin_url
        if self.ags_admin_url.endswith("/"):
            self.ags_admin_url = self.ags_admin_url[:-1]
        self.Tool = tool

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.ags_admin_url, self.username, self.password)
        # create the NTLM authentication handler
        auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)

        # create and install the opener
        opener = urllib2.build_opener(auth_NTLM)
        urllib2.install_opener(opener)

        self.ags_admin_url = self.ags_admin_url + '/arcgis/admin'


    def _requestFromServer(self, adress, params, content_type='application/json', method="POST"):
        """Function for ntlm request creation

        Args:
            self: The reserved object 'self'
            adress: Adress of request
            params: Params as dictionary
            content_type: Http content type
            method: Http method

        Returns:
            Response string
        """
        data = urllib.urlencode(params)
        req = urllib2.Request(self.ags_admin_url + '/' + adress, data=data)
        req.add_header("Content-Type", content_type)
        req.get_method = lambda: method
        response = urllib2.urlopen(req)
        respString = response.read()
        if not response.code == 200:
            raise MyError.MyError("Error: in getting url: {0}?{1} {2} message: {3}".format(self.ags_admin_url + '/' + adress, data, method, response.msg))
        return respString

    def _assertJsonSuccess(self, data):
        """Function for aserting json request state

        Args:
            self: The reserved object 'self'
            data: Request response string

        Returns:
            boolean False if request has errors
        """
        obj = json.loads(data)
        if 'status' in obj and obj['status'] == "error":
            raise MyError.MyError("Error: JSON object returns an error. " + str(obj))
            return False
        else:
            return True

    def _processFolderString(self, folder):
        """Function for processing folder name string

        Args:
            self: The reserved object 'self'
            folder: folder string

        Returns:
            corrected folder string
        """
        if folder == None:
            folder = "ROOT"
        if folder.upper() == "ROOT":
            folder = ""
        else:
            folder += "/"
        return folder

    def startService(self, folder, service):
        self.startStopService(folder, service, "start")

    def stopService(self, folder, service):
        self.startStopService(folder, service, "stop")

    def startStopService(self, folder, service, action):
        # Construct URL to read folder
        folder = self._processFolderString(folder)

        # Define service URL with action (START/STOP)
        folderURL = "services/" + folder + service + "/" + action + '?f=pjson'
        params = {}

        data = self._requestFromServer(folderURL, params)

        # Check that data returned is not an error object
        if not self._assertJsonSuccess(data):
            raise MyError.MyError("Error when reading folder information. " + str(data))
        else:
            if self.Tool != None:
                self.Tool.AddMessage("Service " + folder + service + ' ' + action + ' done successfully ...')

    def getServiceList(self, folder):
        """Retrieve ArcGIS server services

        Args:
            self: The reserved object 'self'
            folder: Folder of the service (ROOT for root services)
        """
        services = []
        folder = self._processFolderString(folder)
        URL = "services/{}?f=pjson".format(folder)
        params = {}
        data = self._requestFromServer(URL, params)

        try:
            serviceList = json.loads(data)
        except urllib2.URLError, e:
            raise MyError.MyError(e)

        # Build up list of services at the root level
        for single in serviceList["services"]:
            services.append(folder + single['serviceName'] + '.' + single['type'])

        # Build up list of folders and remove the System and Utilities folder (we dont want anyone playing with them)
        folderList = serviceList["folders"] if u'folders' in serviceList != False else []
        if u'Utilities' in serviceList != False:
            folderList.remove("Utilities")
        if u'System' in serviceList != False:
            folderList.remove("System")

        if len(folderList) > 0:
            for subfolder in folderList:
                URL = "services/{}?f=pjson".format(subfolder)
                data = self._requestFromServer(URL, params)
                fList = json.loads(data)

                for single in fList["services"]:
                    services.append(subfolder + "//" + single['serviceName'] + '.' + single['type'])

        if len(services) == 0:
            if self.Tool != None:
                self.Tool.AddMessage("No services found")
        else:
            if self.Tool != None:
                self.Tool.AddMessage("Services on " + self.serverurl +":")
            for service in services:
                statusURL = "services/{}/status?f=pjson".format(service)
                data = self._requestFromServer(statusURL, params)
                status = json.loads(data)
                if self.Tool != None:
                    self.Tool.AddMessage("  " + status["realTimeState"] + " > " + service)

        return services

    def GetServerJson(self, server_service):
        """Retrieve service parameters

        Args:
            self: The reserved object 'self'
            serverService: Service which parameter configuration shall be retrieved

        Returns:
            json data object
        """
        serviceURL = "services/" + server_service + '?f=pjson'
        params = {}
        data = self._requestFromServer(serviceURL, params)

        # Check that data returned is not an error object
        if not self._assertJsonSuccess(data):
            raise MyError.MyError(u'...Couldn\'t retrieve service parameter configuration: ' + str(data) + '\n')
        else:
            if self.Tool != None:
                self.Tool.AddMessage(u'...Service parameter configuration successfully retrieved\n')

        dataObj = json.loads(data)
        return dataObj

    def publishServerJson(self, service, dataObj, token, serverPort):
        """Publish service parameters to server

        Args:
            self: The reserved object 'self'
            service: Service which parameter configuration shall be renewed
            dataObj: Parameter configuration
        """

        # Serialize back into JSON
        updatedSvcJson = json.dumps(dataObj)

        # Call the edit operation on the service. Pass in modified JSON.
        editSvcURL = "services/" + service + "/edit?f=pjson"
        params = {'service': updatedSvcJson}
        editData = self._requestFromServer(editSvcURL, params)

        if not self._assertJsonSuccess(editData):
            if self.Tool != None:
                self.Tool.AddMessage(u'...Service configuration renewal error: ' + str(editData) + '\n')
        else:
            if self.Tool != None:
                self.Tool.AddMessage(u'...Service configuration succesfully renewed\n')

        return

    def getServiceFromServer(self, services, service, serviceDir):
        """Retrieve the full service name from the server

        Args:
            self: The reserved object 'self'
            services: List of all services on server
            service: Name of the service from which to get corresponding name from the server services list
            serviceDir: Name of the service directory which is shown in the configuration of services to be published on the server
        """
        if serviceDir == None:
            configService = service
        else:
            configService = serviceDir + "//" + service
        for serverService in services:
            if serverService.split('.')[0].upper() == configService.upper():
                return serverService
            else:
                serverService = ''

        return serverService


    #Check if service is running
    def isServiceRunning(self, folder, service):
        """Retrieve the service status from the server

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service

        Returns: True if is running
        """
        # Construct URL to read folder
        folder = self._processFolderString(folder)
        statusURL = "services/" + folder + service + "/status?f=pjson"
        params = {}
        statusData = self._requestFromServer(statusURL, params, method='GET')

        # Check that data returned is not an error object
        if not self._assertJsonSuccess(statusData):
            raise MyError.MyError("Error while retrieving status information for " + service + ".")

        statusDataObj = json.loads(statusData)
        if statusDataObj['realTimeState'] == "STOPPED":
            return False #print "Service " + service + " was detected to be stopped"
        else:
            return True #print "Service " + service + " is running"
