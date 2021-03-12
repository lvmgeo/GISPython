# -*- coding: utf-8 -*-
"""
     Module for operations with ArcGIS Server services
"""

import urllib
import json
import urllib2
import ssl
import urlparse
from collections import OrderedDict
from ntlm import HTTPNtlmAuthHandler
import MyError

class AGServerHelperNTLM(object):
    """Class for operations with ArcGIS Server services"""

    def __init__(self,
                 username,
                 password,
                 ags_admin_url,
                 tool=None,
                 basic=False,
                 allowunverifiedssl=False):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            username: ArcGIS Server administrator username
            password: ArcGIS Server administrator password
            ags_admin_url: ArcGIS server rest admin url
            Tool: GISPython tool (optional)
            basic: bool indicating that Basic autentification will be used instead of NTLM
        """
        self.username = username
        self.password = password
        self.ags_admin_url = ags_admin_url
        self.serverurl = ags_admin_url
        if self.ags_admin_url.endswith("/"):
            self.ags_admin_url = self.ags_admin_url[:-1]
        self.Tool = tool

        self.ags_admin_url = urlparse.urljoin(self.ags_admin_url, '/arcgis/admin')

        if allowunverifiedssl:
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                # Legacy Python that doesn't verify HTTPS certificates by default
                pass
            else:
                # Handle target environment that doesn't support HTTPS verification
                ssl._create_default_https_context = _create_unverified_https_context

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.ags_admin_url, self.username, self.password)

        if not basic:
            auth_handler = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
        else:
            auth_handler = urllib2.HTTPBasicAuthHandler(passman)

        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)


    def __request_from_server(self, adress, params, content_type='application/json', method="POST"):
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
        url_address = urlparse.urljoin(self.ags_admin_url + "/", adress)
        req = urllib2.Request(url=url_address, data=data)
        req.add_header('Content-Type', content_type)
        req.get_method = lambda: method
        response = urllib2.urlopen(req)
        response_string = response.read()
        if not response.code == 200:
            raise MyError.MyError("Error: in getting url: {0}?{1} {2} message: {3}".format(
                url_address, data, method, response.msg))
        return response_string

    def __assert_json_success(self, data):
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
        else:
            return True

    def __process_folder_string(self, folder):
        """Function for processing folder name string

        Args:
            self: The reserved object 'self'
            folder: folder string

        Returns:
            corrected folder string
        """
        if folder is None:
            folder = "ROOT"
        if folder.upper() == "ROOT":
            folder = ""
        else:
            folder += "/"
        return folder

    def startService(self, folder, service):
        """Starts AGS Service

        Args:
            folder (string): AGS folder of the service. (CASE sensitive) Use ROOT for services without folder.
            service (string): Service name (CASE sensitive)
        """
        self.__start_stop_service(folder, service, "start")

    def stopService(self, folder, service):
        """Stops AGS Service

        Args:
            folder (string): AGS folder of the service. (CASE sensitive) Use ROOT for services without folder.
            service (string): Service name (CASE sensitive)
        """
        self.__start_stop_service(folder, service, "stop")

    def __start_stop_service(self, folder, service, action):
        folder = self.__process_folder_string(folder)
        folder_url = "services/" + folder + service + "/" + action + '?f=json'
        params = {}
        data = self.__request_from_server(folder_url, params)

        if not self.__assert_json_success(data):
            raise MyError.MyError("Error when reading folder information. " + str(data))
        else:
            if self.Tool != None:
                self.Tool.AddMessage("Service {}{} {}  done successfully ...".format(
                    folder, service, action))

    def getServiceList(self, folder, return_running_state=True):
        """Retrieve ArcGIS server services

        Args:
            self: The reserved object 'self'
            folder: Folder of the service (ROOT for root services)
        """
        services = []
        folder = self.__process_folder_string(folder)
        url = "services/{}?f=json".format(folder)
        params = {}
        data = self.__request_from_server(url, params)

        try:
            service_list = json.loads(data)
        except urllib2.URLError, exception:
            raise MyError.MyError(exception)

        for single in service_list["services"]:
            services.append(folder + single['serviceName'] + '.' + single['type'])

        folder_list = service_list["folders"] if u'folders' in service_list != False else []
        if u'Utilities' in service_list != False:
            folder_list.remove("Utilities")
        if u'System' in service_list != False:
            folder_list.remove("System")

        if folder_list:
            for subfolder in folder_list:
                url = "services/{}?f=json".format(subfolder)
                data = self.__request_from_server(url, params)
                subfolder_list = json.loads(data)

                for single in subfolder_list["services"]:
                    services.append(subfolder + "//" + single['serviceName'] + '.' + single['type'])

        if not services:
            if self.Tool != None:
                self.Tool.AddMessage("No services found")
        else:
            if self.Tool != None:
                self.Tool.AddMessage("Services on " + self.serverurl +":")
            for service in services:
                if return_running_state:
                    status_url = "services/{}/status?f=json".format(service)
                    data = self.__request_from_server(status_url, params)
                    status = json.loads(data)
                    if self.Tool != None:
                        self.Tool.AddMessage("  " + status["realTimeState"] + " > " + service)
                else:
                    if self.Tool != None:
                        self.Tool.AddMessage(" > " + service)

        return services

    def GetServerJson(self, server_service):
        """Retrieve service parameters

        Args:
            self: The reserved object 'self'
            serverService: Service which parameter configuration shall be retrieved

        Returns:
            json data object
        """
        service_url = "services/" + server_service + "?f=json"
        params = {}
        data = self.__request_from_server(service_url, params, method='GET')

        if not self.__assert_json_success(data):
            raise MyError.MyError(
                u'...Couldn\'t retrieve service parameter configuration: {}\n'.format(data))
        else:
            if self.Tool != None:
                self.Tool.AddMessage(u'...Service parameter configuration successfully retrieved\n')

        data_object = json.loads(data)
        return data_object

    def publishServerJson(self, service, data_object):
        """Publish service parameters to server

        Args:
            self: The reserved object 'self'
            service: Service which parameter configuration shall be renewed
            data_object: Parameter configuration
        """

        updated_svc_json = json.dumps(data_object)
        edit_svc_url = "services/" + service + "/edit"
        params = {'f': 'json', 'service': updated_svc_json}
        edit_data = self.__request_from_server(edit_svc_url,
                                               params,
                                               'application/x-www-form-urlencoded',
                                               method='POST')

        if not self.__assert_json_success(edit_data):
            if self.Tool != None:
                self.Tool.AddMessage(
                    u'...Service configuration renewal error: {}\n'.format(edit_data))
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
        server_service = ''
        if serviceDir is None:
            config_service = service
        else:
            config_service = serviceDir + "/" + service
        for server_service in services:
            if server_service.split('.')[0].upper() == config_service.upper():
                return server_service

        return ''

    def getServicePermisions(self, folder, service):
        """Check service permisions

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service

        Returns: Dictionary of service principals
        """
        folder = self.__process_folder_string(folder)
        status_url = "services/" + folder + service + "/permissions?f=pjson"
        params = {}
        permisions_data = self.__request_from_server(status_url, params, method='GET')

        if not self.__assert_json_success(permisions_data):
            raise MyError.MyError(
                "Error while retrieving permisions information for {}.".format(service))

        statusdata_object = json.loads(permisions_data)
        return_dict = OrderedDict()
        for permision in statusdata_object["permissions"]:
            principal = permision["principal"]
            if permision.has_key("permission"):
                if permision["permission"].has_key("isAllowed"):
                    return_dict[principal] = permision["permission"]["isAllowed"]
                else:
                    return_dict[principal] = True
        return return_dict

    def addServicePermisions(self, folder, service, principal, is_allowed='true'):
        """Add service permisions

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service
            principal: The name of the role for whom the permission is being assigned.
            is_allowed: Tells if access to a resource is allowed or denied.
        """
        urlparams = urllib.urlencode({'principal':principal, 'isAllowed':is_allowed, 'f':'json'})
        folder = self.__process_folder_string(folder)
        status_url = "services/" + folder + service + "/permissions/add?{}".format(urlparams)
        params = {}
        permisions_data = self.__request_from_server(status_url, params, method='POST')

        if not self.__assert_json_success(permisions_data):
            raise MyError.MyError(
                "Error while setting permisions information for {} to {}.".format(
                    service, principal))

    def isServiceRunning(self, folder, service):
        """Check if service is running

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service

        Returns: True if is running
        """
        folder = self.__process_folder_string(folder)
        status_url = "services/" + folder + service + "/status?f=json"
        params = {}
        status_data = self.__request_from_server(status_url, params, method='GET')

        if not self.__assert_json_success(status_data):
            raise MyError.MyError(
                "Error while retrieving status information for {}.".format(service))

        statusdata_object = json.loads(status_data)
        if statusdata_object['realTimeState'] == "STOPPED":
            return False
        else:
            return True

    def GetDatasetNames(self, folder, service):
        """Retrieve the service Dataset Names from the server

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service

        Returns: list of strings
        """
        folder = self.__process_folder_string(folder)
        manifest_url = "services/" + folder + service + "/iteminfo/manifest/manifest.json?f=json"
        params = {}
        status_data = self.__request_from_server(manifest_url, params, method='GET')
        rezult = list()

        if not self.__assert_json_success(status_data):
            raise MyError.MyError(
                "Error while retrieving manifest information for {}.".format(service))

        statusdata_object = json.loads(status_data)
        for database in statusdata_object['databases']:
            rezult.append(database['onServerName'])

        return rezult

    def getRoles(self, pageSize=5000):
        """Retrieve the Role Names from the server

        Args:
            self: The reserved object 'self'

        Returns: list of strings
        """
        manifest_url = "security/roles/getRoles?startIndex=0&pageSize={}&f=json".format(pageSize)
        params = {}
        roles_data = self.__request_from_server(manifest_url, params, method='POST')
        rezult = list()

        if not self.__assert_json_success(roles_data):
            raise MyError.MyError("Error while retrieving role information.")

        roles = json.loads(roles_data)
        for role in roles['roles']:
            if role.has_key("description"):
                rezult.append({"rolename": role["rolename"],
                               "description": role["description"]})
            else:
                rezult.append({"rolename": role["rolename"]})


        return rezult

    def addRole(self, rolename, description=''):
        """Retrieve the Role Names from the server

        Args:
            self: The reserved object 'self'
            rolename: The name of the role. The name must be unique in the role store.
        """
        urlparams = urllib.urlencode({'rolename':rolename, 'description':description, 'f':'json'})
        manifest_url = "security/roles/add?{}".format(urlparams)
        params = {}
        roles_data = self.__request_from_server(manifest_url, params, method='POST')

        if not self.__assert_json_success(roles_data):
            raise MyError.MyError("Error while adding role {}".format(rolename))

    def removeRole(self, rolename):
        """Retrieve the Role Names from the server

        Args:
            self: The reserved object 'self'
            rolename: The name of the role.
        """
        urlparams = urllib.urlencode({'rolename':rolename, 'f':'json'})
        manifest_url = "security/roles/remove?{}".format(urlparams)
        params = {}
        roles_data = self.__request_from_server(manifest_url, params, method='POST')

        if not self.__assert_json_success(roles_data):
            raise MyError.MyError("Error while removing role {}".format(rolename))

    def getUsersWithinRole(self, rolename, maxCount=5000):
        """Retrieve the Role Names from the server

        Args:
            self: The reserved object 'self'

        Returns: list of strings
        """
        urlparams = urllib.urlencode({'rolename':rolename, 'maxCount':maxCount, 'f':'json'})
        manifest_url = "security/roles/getUsersWithinRole?{}".format(urlparams)
        params = {}
        users_data = self.__request_from_server(manifest_url, params, method='POST')
        rezult = list()

        if not self.__assert_json_success(users_data):
            raise MyError.MyError("Error while retrieving role user information.")

        users = json.loads(users_data)
        for user in users['users']:
            rezult.append(user)

        return rezult

    def addUsersToRole(self, rolename, users):
        """assign a role to multiple users with a single action

        Args:
            self: The reserved object 'self'
            rolename: The name of the role.
            users: A comma-separated list of user names. Each user name must exist in the user store.
        """
        urlparams = urllib.urlencode({'rolename':rolename, 'users':users, 'f':'json'})
        manifest_url = "security/roles/addUsersToRole?{}".format(urlparams)
        params = {}
        roles_data = self.__request_from_server(manifest_url, params, method='POST')

        if not self.__assert_json_success(roles_data):
            raise MyError.MyError(
                "Error while adding users [{1}] to a role {0}".format(rolename, users))

    def removeUsersFromRole(self, rolename, users):
        """Removes a role assignment from multiple users

        Args:
            self: The reserved object 'self'
            rolename: The name of the role.
            users: A comma-separated list of user names. Each user name must exist in the user store.
        """
        urlparams = urllib.urlencode({'rolename':rolename, 'users':users, 'f':'json'})
        manifest_url = "security/roles/removeUsersFromRole?{}".format(urlparams)
        params = {}
        roles_data = self.__request_from_server(manifest_url, params, method='POST')

        if not self.__assert_json_success(roles_data):
            raise MyError.MyError(
                "Error while removing users [{1}] from a role {0}".format(rolename, users))

    def GetDatasetNamesWithObjects(self, folder, service):
        """Retrieve the service Dataset Names from the server

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service

        Returns: list of strings
        """
        folder = self.__process_folder_string(folder)
        manifest_url = "services/" + folder + service + "/iteminfo/manifest/manifest.json?f=json"
        params = {}
        status_data = self.__request_from_server(manifest_url, params, method='GET')
        rezult = list()

        if not self.__assert_json_success(status_data):
            raise MyError.MyError("Error while retrieving manifest information for " + service + ".")

        statusdata_object = json.loads(status_data)
        for database in statusdata_object['databases']:
            dataset_names = [d['onServerName'] for d in database['datasets']]
            item = {"database": database['onServerName'], "datasets":dataset_names}
            rezult.append(item)

        return rezult

    def GetRightsGroupsNames(self, folder, service):
        """Retrieve the service permission role names from service

        Args:
            self: The reserved object 'self'
            folder: Service directory
            service: Name of a service

        Returns: list of strings
        """
        folder = self.__process_folder_string(folder)
        manifest_url = "services/" + folder + service + "/permissions?f=json"
        params = {}
        status_data = self.__request_from_server(manifest_url, params, method='GET')
        rezult = list()

        if not self.__assert_json_success(status_data):
            raise MyError.MyError(
                "Error while retrieving permissions information for {}.".format(service))

        permissions = json.loads(status_data)
        for permission in permissions['permissions']:
            rezult.append(permission['principal'])

        return rezult

    def GetServiceInfo(self, folder):
        """Retrieve the Folder List from the server

        Args:
            self: The reserved object 'self'
            folder: Service directory

        Returns: list of service objects
        """
        folder = self.__process_folder_string(folder)
        manifest_url = "services/" + folder + "/?f=json"
        params = {}
        status_data = self.__request_from_server(manifest_url, params, method='GET')
        rezult = list()

        if not self.__assert_json_success(status_data):
            raise MyError.MyError("Error while retrieving folder information.")

        statusdata_object = json.loads(status_data)
        rezult.append(statusdata_object)
        folderlist = list()
        for folder_detail in statusdata_object['foldersDetail']:
            folderlist.append(folder_detail['folderName'])

        for subfolder in folderlist:
            if not (subfolder.upper() == 'System'.upper()
                    or subfolder.upper() == 'Utilities'.upper()):
                manifest_url = "services/" + subfolder + "/?f=json"
                status_data = self.__request_from_server(manifest_url, params, method='GET')
                statusdata_object = json.loads(status_data)
                rezult.append(statusdata_object)

        return rezult
