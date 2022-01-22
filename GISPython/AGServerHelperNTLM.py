# -*- coding: utf-8 -*-
"""
     Module for operations with ArcGIS Server services
"""

import os
import urllib
import json
import urllib2
import ssl
import urlparse
import tempfile
from lxml import etree
from collections import OrderedDict
from ntlm import HTTPNtlmAuthHandler

import MyError
import TimerHelper


class AGServerHelperNTLM(object):
    """Class for operations with ArcGIS Server services"""

    def __init__(self,
                 username,
                 password,
                 ags_admin_url,
                 tool=None,
                 basic=False,
                 allowunverifiedssl=False,
                 token=False
                 ):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            username: ArcGIS Server administrator username
            password: ArcGIS Server administrator password
            ags_admin_url: ArcGIS server rest admin url
            tool: GISPython tool (optional)
            basic: bool indicating that Basic autentification will be used instead of NTLM
            allowunverifiedssl: bool indicating that unsecure SSL connections are allowed
            token: bool indicating that token authentication is to be used
        """
        self.username = username
        self.password = password
        self.ags_admin_url = ags_admin_url
        self.server_url = ags_admin_url

        if self.ags_admin_url.endswith("/"):
            self.ags_admin_url = self.ags_admin_url[:-1]

        self.Tool = tool

        self.ags_admin_url = urlparse.urljoin(self.ags_admin_url, '/arcgis/admin')

        if allowunverifiedssl:
            self._set_allow_unsafe_ssl()

        self.authentication_mode = 'ntlm'
        if basic:
            self.authentication_mode = 'basic'
        if token:
            self.authentication_mode = 'token'

        if self.authentication_mode in ('ntlm', 'basic'):
            self._set_autentification_handler()
        else:
            self.token = self._generate_tocken()
            if self.token == "":
                raise MyError.MyError("Could not generate a token with the username and password provided.")

    def _set_autentification_handler(self):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.ags_admin_url, self.username, self.password)
        if self.authentication_mode == 'ntlm':
            auth_handler = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
        else:
            auth_handler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

    @staticmethod
    def _set_allow_unsafe_ssl():
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    def _generate_tocken(self, expiration=60 * 24):
        query_dict = {
            'username': self.username,
            'password': self.password,
            'expiration': expiration,
            'client': 'requestip'}

        query_string = urllib.urlencode(query_dict)
        url = "{}/generateToken".format(self.ags_admin_url)

        token = json.loads(urllib.urlopen(url + "?f=json", query_string).read())

        if "token" not in token:
            raise MyError.MyError(token['messages'])
        else:
            return token['token']

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
        if self.authentication_mode == 'token':
            if method == "POST":
                if params is None:
                    params = {'token': self.token}
                else:
                    params['token'] = self.token

            if '?' in adress:
                adress = u'{}&token={}'.format(adress, self.token)
            else:
                adress = u'{}?token={}'.format(adress, self.token)

        data = urllib.urlencode(params)
        url_address = urlparse.urljoin(self.ags_admin_url + "/", adress)
        print(url_address)
        req = urllib2.Request(url=url_address, data=data)
        req.add_header('Content-Type', content_type)
        req.get_method = lambda: method
        response = urllib2.urlopen(req)
        response_string = response.read()
        if not response.code == 200:
            raise MyError.MyError("Error: in getting url: {0}?{1} {2} message: {3}".format(
                url_address, data, method, response.msg))
        return response_string

    @staticmethod
    def __assert_json_success(data):
        obj = json.loads(data)
        if 'status' in obj and obj['status'] == "error":
            raise MyError.MyError("Error: JSON object returns an error. " + str(obj))
        else:
            return True

    @staticmethod
    def __process_folder_string(folder):
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
            self._add_message("Service {}{} {}  done successfully ...".format(
                folder, service, action))

    def getServiceList(self, folder, return_running_state=True):
        """Retrieve ArcGIS server services

        Args:
            folder: Folder of the service (ROOT for root services)
            return_running_state: If False no service running state will be checked (works faster)
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

        folder_list = service_list["folders"] if u'folders' in service_list else []
        if u'Utilities' in service_list:
            folder_list.remove("Utilities")
        if u'System' in service_list:
            folder_list.remove("System")

        if folder_list:
            for subfolder in folder_list:
                url = "services/{}?f=json".format(subfolder)
                data = self.__request_from_server(url, params)
                subfolder_list = json.loads(data)

                for single in subfolder_list["services"]:
                    services.append(subfolder + "/" + single['serviceName'] + '.' + single['type'])

        if not services:
            self._add_message("No services found")
        else:
            self._add_message("Services on " + self.server_url + ":")
            for service in services:
                if return_running_state:
                    status_url = "services/{}/status?f=json".format(service)
                    data = self.__request_from_server(status_url, params)
                    status = json.loads(data)
                    self._add_message("  " + status["realTimeState"] + " > " + service)
                else:
                    self._add_message(" > " + service)

        return services

    def GetServerJson(self, server_service):
        """Retrieve service parameters

        Args:
            self: The reserved object 'self'
            server_service: Service which parameter configuration shall be retrieved

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
            self._add_message(u'...Service parameter configuration successfully retrieved\n')

        data_object = json.loads(data)
        return data_object

    def publishServerJson(self, service, data_object, gp=None):
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
            self._add_message(
                u'...Service configuration renewal error: {}\n'.format(edit_data), gp)
        else:
            self._add_message(u'...Service configuration succesfully renewed\n')

        return

    def getServiceFromServer(self, services, service, serviceDir):
        """Retrieve the full service name from the server

        Args:
            self: The reserved object 'self'
            services: List of all services on server
            service: Name of the service from which to get corresponding name from the server services list
            serviceDir: Name of the service directory which is shown in the configuration of services to be published on the server
        """
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
            if "permission" in permision:
                if "isAllowed" in permision["permission"]:
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
        urlparams = urllib.urlencode({'principal': principal, 'isAllowed': is_allowed, 'f': 'json'})
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
            pageSize: The maximums records rturned

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
            if "description" in role:
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
        urlparams = urllib.urlencode({'rolename': rolename, 'description': description, 'f': 'json'})
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
        urlparams = urllib.urlencode({'rolename': rolename, 'f': 'json'})
        manifest_url = "security/roles/remove?{}".format(urlparams)
        params = {}
        roles_data = self.__request_from_server(manifest_url, params, method='POST')

        if not self.__assert_json_success(roles_data):
            raise MyError.MyError("Error while removing role {}".format(rolename))

    def getUsersWithinRole(self, rolename, maxCount=5000):
        """Retrieve the Role Names from the server

        Args:
            self: The reserved object 'self'
            maxCount: maximum returned record count

        Returns: list of strings
        """
        urlparams = urllib.urlencode({'rolename': rolename, 'maxCount': maxCount, 'f': 'json'})
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
        urlparams = urllib.urlencode({'rolename': rolename, 'users': users, 'f': 'json'})
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
        urlparams = urllib.urlencode({'rolename': rolename, 'users': users, 'f': 'json'})
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
            item = {"database": database['onServerName'], "datasets": dataset_names}
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

    def publish_mxd(self, mxd, service, service_folder, arcgis_server_connection, gp, create_new=False,
                    aditional_params={}):
        """Publishes MXD to server

        Args:
            self: The reserved object 'self'
            mxd: MXD document name
            service: AGS service name
            service_folder: AGS service folder
            create_new: create new AGS service?
            arcgis_server_connection: path to ArcGIS Server connection file *.ags
            gp: ArcPy object
            create_new: bool True if new service can be created if service does not exist
            aditional_params: (example)
                [
                    {
                        'TypeName': 'MapServer',
                        'ConfigurationProperties': {
                            'enableDynamicLayers': 'false',
                            'maxDomainCodeCount': '250000'

                        },
                        "Props": {
                            'MaxInstances': '10'
                        }
                    },
                    {
                        'TypeName': 'KmlServer',
                        'Enabled': 'false'
                    },
                    {
                        'TypeName': 'FeatureServer',
                        'Enabled': 'true',
                        "Props": {
                            'maxRecordCount': '2000'
                        }
                    }
                ]
        """
        service_exists = True

        server_admin_temp = tempfile.gettempdir()
        mxd_name = os.path.splitext(os.path.basename(mxd))[0]
        sdd_draft = os.path.join(server_admin_temp, mxd_name) + '.sddraft'
        sd = os.path.join(server_admin_temp, mxd_name) + '.sd'

        timer = TimerHelper.TimerHelper()

        self._add_message(
            u'\n...Processing MXD file [{}] and preparing service for publish\n'.format(mxd), gp)

        services = self.getServiceList(service_folder, False)
        server_service = self.getServiceFromServer(services, service, service_folder)

        if server_service == '':
            service_exists = False

        if not service_exists and not create_new:
            self._add_warning(
                u'\n===================================\n...Service [' + service + u'] does not exist on server!\n===================================\n')
            return False

        json_data = self.GetServerJson(server_service)

        self._add_message(u'...Creating SDDraft: {} - {}\n'.format(sdd_draft, timer.GetTimeReset()), gp)

        mxd = gp.mapping.MapDocument(mxd)
        gp.mapping.CreateMapSDDraft(
            mxd, sdd_draft, service, 'ARCGIS_SERVER',
            os.path.join(server_admin_temp, arcgis_server_connection), False, service_folder)

        gp.env.overwriteOutput = True
        self._correct_sdd_draft_configuration(sdd_draft, service_exists, aditional_params)

        self._add_message(u'...Start SDDraft validation {}\n'.format(timer.GetTimeReset()), gp)
        analysis = gp.mapping.AnalyzeForSD(sdd_draft)

        error_code = self._print_sdd_analysis_results(analysis, sdd_draft, gp)

        if analysis['errors'] == {} and error_code != 24011 and error_code != 24012:
            self._add_message(
                u'...SDDraft validation no critical problems where found - {}\n'.format(timer.GetTimeReset()), gp)
            self._add_message(u'...Start creating stage service \n', gp)

            gp.StageService_server(sdd_draft, sd)

            self._add_message(u'...Start publishing service {}\n'.format(timer.GetTimeReset()), gp)
            gp.UploadServiceDefinition_server(sd, os.path.join(server_admin_temp, arcgis_server_connection))

            if not service_exists:
                self._add_message(
                    u'...Server did not contain service, and service has been created: {}'.format(service), gp)
                return True
            else:
                self._renew_service_configuration(json_data, server_service, timer, gp)
                return True
        else:
            self._add_message(
                u'...SDDraft file validation critical errors found {}'.format(timer.GetTimeReset()), gp)
            return False

    @staticmethod
    def _correct_sdd_draft_configuration(sdd_draft, service_exists, aditional_params):
        xml = etree.parse(sdd_draft)
        # xml.write(sdd_draft, pretty_print=True, method="xml", xml_declaration=True, encoding="utf-8")

        if service_exists:
            xml.xpath('/SVCManifest/Type')[0].text = 'esriServiceDefinitionType_Replacement'
        xml.xpath('/SVCManifest/State')[0].text = 'esriSDState_Published'

        if aditional_params is not None and aditional_params:
            for extension_config in aditional_params:
                if extension_config['TypeName'] == 'MapServer':
                    extension_tag = xml.xpath(
                        '/SVCManifest/Configurations/SVCConfiguration/TypeName[text()="{}"]/..'.format(
                            extension_config['TypeName']))[0]
                    if 'ConfigurationProperties' in extension_config:
                        for config_property, property_value in extension_config['ConfigurationProperties'].items():
                            extension_tag.xpath(
                                './Definition/ConfigurationProperties/PropertyArray/PropertySetProperty/Key[text()="{}"]/../Value'.format(
                                    config_property))[0].text = property_value
                    if 'Props' in extension_config:
                        for config_property, property_value in extension_config['Props'].items():
                            extension_tag.xpath(
                                './Definition/Props/PropertyArray/PropertySetProperty/Key[text()="{}"]/../Value'.format(
                                    config_property))[0].text = property_value
                else:
                    extension_tag = xml.xpath(
                        '/SVCManifest/Configurations/SVCConfiguration/Definition/Extensions/SVCExtension/TypeName[text()="{}"]/..'.format(
                            extension_config['TypeName']))[0]
                    if 'Enabled' in extension_config:
                        extension_tag.xpath('./Enabled')[0].text = extension_config['Enabled']
                    if 'Props' in extension_config:
                        for config_property, property_value in extension_config['Props'].items():
                            extension_tag.xpath(
                                './Props/PropertyArray/PropertySetProperty/Key[text()="{}"]/../Value'.format(
                                    config_property))[0].text = property_value

        xml.write(sdd_draft, pretty_print=True, method="xml", xml_declaration=True, encoding="utf-8")

    def _print_sdd_analysis_results(self, analysis, sdd_draft, gp):
        error_code = 0
        iterable_keys = [key for key in ('messages', 'warnings', 'errors') if analysis[key] != {}]
        for key in iterable_keys:
            self._add_message("---" + key.upper() + "---", gp)
            collection = analysis[key]
            for ((message, code), layerlist) in collection.iteritems():
                laystr = ', '.join([layer.name for layer in layerlist])
                text = u"    [{0}] - {1}".format(code, message)
                if unicode(laystr) != '':
                    text = text + u"Applies to: ({0})".format(laystr)
                if key == 'messages':
                    self._add_message(text, gp)
                if key == 'warnings':
                    self._add_message(text, gp)
                    if code == 24011 or code == 24012:
                        error_code = code
                        self._add_warning(
                            u'...\n===================================================\nData source not reggistered on server. To prevent data copy on server - publish will stop: {}\n==================================================='.format(
                                sdd_draft), gp)
                if key == 'errors':
                    self._add_error(text)
        return error_code

    def _renew_service_configuration(self, json_data, server_service, timer, gp):
        self._add_message(u'...read new config from server - {}\n'.format(timer.GetTimeReset()))
        new_json_data = self.GetServerJson(server_service)
        json_data["datasets"] = new_json_data["datasets"]
        self.publishServerJson(server_service, json_data, gp)
        self._add_message(
            u'...Service configuration on server updated {}'.format(timer.GetTimeReset()), gp)

    @staticmethod
    def _set_tag_data_values(doc, tag_name, parent_tag_name, data):
        type_tags = doc.getElementsByTagName(tag_name)
        for tag in type_tags:
            if tag.parentNode.tagName == parent_tag_name:
                if tag.hasChildNodes():
                    tag.firstChild.data = data

    def _add_message(self, message, gp=None):
        if self.Tool is not None:
            self.Tool.AddMessage(message)
        elif gp is not None:
            gp.AddMessage(message)
        else:
            print message

    def _add_warning(self, message, gp=None):
        if self.Tool is not None:
            self.Tool.AddWarning(message)
        elif gp is not None:
            gp.AddWarning(message)
        else:
            print message

    def _add_error(self, message, gp=None):
        if self.Tool is not None:
            self.Tool.AddError(message)
        elif gp is not None:
            gp.AddError(message)
        else:
            print message
