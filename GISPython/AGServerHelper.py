# -*- coding: utf-8 -*-
"""
     Module for operations with ArcGIS Server services
"""

# For Http calls
import httplib, urllib, json, urllib2
import MyError

class AGSServerHelper(object):

    def __init__(self, username, password, serverName, serverPort=6080, Tool=None, https=False):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            username: ArcGIS Server administrator username
            password: ArcGIS Server administrator password
            serverName: Server adress
            serverPort: Server port (optional)
            Tool: GISPython tool (optional)
        """
        self.username = username
        self.password = password
        self.serverName = serverName
        self.serverPort = serverPort
        self.Tool = Tool
        self.https = https
        if https:
            self.httstring = 'https'
        else:
            self.httstring = 'http'
        # Get a token
        self.token = self.genToken(username, password, serverName, serverPort)
        if self.token == "":
            raise MyError.MyError("Could not generate a token with the username and password provided.")

    def StartService(self, folder, service):
        self.StartStopService(folder, service, "START")

    def StopService(self, folder, service):
        self.StartStopService(folder, service, "STOP")

    def StartStopService(self, folder, service, action):
        # Construct URL to read folder
        if folder == None:
            folder = "ROOT"
        if folder.upper() == "ROOT":
            folder = ""
        else:
            folder += "/"

        # Define service URL with action (START/STOP)
        folderURL = "/arcgis/admin/services/" + folder + service + "/" + action

        # This request only needs the token and the response formatting parameter
        params = urllib.urlencode({'token': self.token, 'f': 'json'})

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        # Connect to URL and post parameters
        if self.https:
            httpConn = httplib.HTTPSConnection(self.serverName, self.serverPort)
        else:
            httpConn = httplib.HTTPConnection(self.serverName, self.serverPort)
        httpConn.request("POST", folderURL, params, headers)

        # Read response
        response = httpConn.getresponse()
        if response.status != 200:
            httpConn.close()
            raise MyError.MyError("Could not read folder information.")
        else:
            data = response.read()

            # Check that data returned is not an error object
            if not self.assertJsonSuccess(data):
                raise MyError.MyError("Error when reading folder information. " + str(data))
            else:
                if self.Tool != None:
                    self.Tool.AddMessage("Service " + folder + service + ' ' + action + ' done successfully ...')

            # Deserialize response into Python object
            #dataObj = json.loads(data)
            httpConn.close()

    def genToken(self, adminUser, adminPass, server, port, expiration=60):
        """Create ArcGIS server connection file

        Args:
            server: Server name
            port: Server port
            adminUser: Username
            adminPass: Password
        """
        query_dict = {'username':   adminUser,
                      'password':   adminPass,
                      'expiration': expiration,
                      'client':     'requestip'}

        query_string = urllib.urlencode(query_dict)
        url = "{}://{}:{}/arcgis/admin/generateToken".format(self.httstring, server, port)

        token = json.loads(urllib.urlopen(url + "?f=json", query_string).read())

        if "token" not in token:
            raise MyError.MyError(token['messages'])
            exit()
        else:
            return token['token']

    def getServiceList(self, server, port, adminUser, adminPass, token=None):
        """Retrieve ArcGIS server services

        Args:
            self: The reserved object 'self'
            server: Server name
            port: Server port
            adminUser: Username
            adminPass: Password
            token: Token (if created)
        """
        if token is None:
            token = self.genToken(adminUser, adminPass, server, port)

        services = []
        folder = ''
        URL = "{}://{}:{}/arcgis/admin/services{}?f=pjson&token={}".format(self.httstring, server, port, folder, token)

        try:
            serviceList = json.loads(urllib2.urlopen(URL).read())
        except urllib2.URLError, e:
            raise MyError.MyError(e)

        # Build up list of services at the root level
        for single in serviceList["services"]:
            services.append(single['serviceName'] + '.' + single['type'])

        # Build up list of folders and remove the System and Utilities folder (we dont want anyone playing with them)
        folderList = serviceList["folders"]
        folderList.remove("Utilities")
        folderList.remove("System")

        if len(folderList) > 0:
            for folder in folderList:
                URL = "{}://{}:{}/arcgis/admin/services/{}?f=pjson&token={}".format(self.httstring, server, port, folder, token)
                fList = json.loads(urllib2.urlopen(URL).read())

                for single in fList["services"]:
                    services.append(folder + "//" + single['serviceName'] + '.' + single['type'])

        if len(services) == 0:
            if self.Tool != None:
                self.Tool.AddMessage("No services found")
        else:
            if self.Tool != None:
                self.Tool.AddMessage("Services on " + server +":")
            for service in services:
                statusURL = "{}://{}:{}/arcgis/admin/services/{}/status?f=pjson&token={}".format(self.httstring, server, port, service, token)
                status = json.loads(urllib2.urlopen(statusURL).read())
                if self.Tool != None:
                    self.Tool.AddMessage("  " + status["realTimeState"] + " > " + service)

        return services

    def GetServerJson(self, token, serverName, serverPort, serverService):
        """Retrieve service parameters

        Args:
            self: The reserved object 'self'
            token: Token
            serverName: Server name
            serverPort: Server port
            serverService: Service which parameter configuration shall be retrieved
        """
        # This request only needs the token and the response formatting parameter
        params = urllib.urlencode({'token': token, 'f': 'json'})

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        serviceURL = "/arcgis/admin/services/" + serverService

        # Connect to service to get its current JSON definition
        if self.https:
            httpConn = httplib.HTTPSConnection(serverName, serverPort)
        else:
            httpConn = httplib.HTTPConnection(serverName, serverPort)
        httpConn.request("POST", serviceURL, params, headers)

        # Read response
        response = httpConn.getresponse()
        if response.status != 200:
            httpConn.close()
            raise MyError.MyError(u'...Couldn\'t retrieve service parameter configuration\n')
            return
        else:
            data = response.read()

            # Check that data returned is not an error object
            if not self.assertJsonSuccess(data):
                raise MyError.MyError(u'...Couldn\'t retrieve service parameter configuration: ' + str(data) + '\n')
            else:
                if self.Tool != None:
                    self.Tool.AddMessage(u'...Service parameter configuration successfully retrieved\n')

        dataObj = json.loads(data)
        httpConn.close()
        return dataObj

    def PublishServerJson(self, service, serverName, dataObj, token, serverPort):
        """Publish service parameters to server

        Args:
            self: The reserved object 'self'
            service: Service which parameter configuration shall be renewed
            serverName: Server name
            dataObj: Parameter configuration
            token: Token
            serverPort: Server port
        """
        if self.https:
            httpConn = httplib.HTTPSConnection(serverName, serverPort)
        else:
            httpConn = httplib.HTTPConnection(serverName, serverPort)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        # Serialize back into JSON
        updatedSvcJson = json.dumps(dataObj)

        # Call the edit operation on the service. Pass in modified JSON.
        editSvcURL = "/arcgis/admin/services/" + service + "/edit"
        params = urllib.urlencode({'token': token, 'f': 'json', 'service': updatedSvcJson})
        httpConn.request("POST", editSvcURL, params, headers)

        # Read service edit response
        editResponse = httpConn.getresponse()
        if editResponse.status != 200:
            httpConn.close()
            if self.Tool != None:
                self.Tool.AddMessage(u'...Service configuration renewal error\n')
            return
        else:
            editData = editResponse.read()

            # Check that data returned is not an error object
            if not self.assertJsonSuccess(editData):
                if self.Tool != None:
                    self.Tool.AddMessage(u'...Service configuration renewal error: ' + str(editData) + '\n')
            else:
                if self.Tool != None:
                    self.Tool.AddMessage(u'...Service configuration succesfully renewed\n')

        httpConn.close()

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

    def assertJsonSuccess(self, data):
        """A function that checks that the input JSON object is not an error object.

        Args:
            self: The reserved object 'self'
            data: JSON data object
        """
        obj = json.loads(data)
        if 'status' in obj and obj['status'] == "error":
            raise MyError.MyError("Error: JSON object returns an error. " + str(obj))
            return False
        else:
            return True

    #Check if service is running
    def IsServiceRunning(self, folder, service):
        """Retrieve the service status from the server

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service
        """
        # Construct URL to read folder
        if folder == None:
            folder = "ROOT"
        if folder.upper() == "ROOT":
            folder = ""
        else:
            folder += "/"

        folderURL = "/arcgis/admin/services/" + folder

        # This request only needs the token and the response formatting parameter
        params = urllib.urlencode({'token': self.token, 'f': 'json'})

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        # Connect to URL and post parameters
        if self.https:
            httpConn = httplib.HTTPSConnection(self.serverName, self.serverPort)
        else:
            httpConn = httplib.HTTPConnection(self.serverName, self.serverPort)

        httpConn.request("POST", folderURL, params, headers)

        # Read response
        response = httpConn.getresponse()
        if response.status != 200:
            httpConn.close()
            raise MyError.MyError("Could not read folder information.")
        else:
            data = response.read()

        # Check that data returned is not an error object
        if not self.assertJsonSuccess(data):
            raise MyError.MyError("Error while reading folder information. " + str(data))

        # Deserialize response into Python object
        dataObj = json.loads(data)

        httpConn.close()

        # Construct URL to stop or start service, then make the request
        statusURL = "/arcgis/admin/services/" + folder + service + "/status"
        httpConn.request("POST", statusURL, params, headers)

        # Read status response
        statusResponse = httpConn.getresponse()
        if statusResponse.status != 200:
            httpConn.close()
            raise MyError.MyError("Error while checking status for " + service)
            return
        else:
            statusData = statusResponse.read()

            # Check that data returned is not an error object
            if not self.assertJsonSuccess(statusData):
                raise MyError.MyError("Error while retrieving status information for " + service + ".")
            else:
                # Get service status
                statusDataObj = json.loads(statusData)
                if statusDataObj['realTimeState'] == "STOPPED":
                    return False #print "Service " + service + " was detected to be stopped"
                else:
                    return True #print "Service " + service + " is running"

            httpConn.close()
