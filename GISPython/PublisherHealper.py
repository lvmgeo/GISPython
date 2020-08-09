# -*- coding: utf-8 -*-
"""
     Deployment publishing operations module
"""

import codecs
import os
import shutil
import hashlib
import datetime
import ZipHelper
import xmlParamsHealper
import JsonParamsHelper

class PublisherHealperConfig:
    """Class for setting up publisher Healper"""
    moduleName = "" # name of the module to be processing
    destinationDir = "" # folder to deploy to
    sourceDir = "" # folder from with to deploy
    doBackup = False # does publisher need to make a backup
    backupFolder = "" # folder in witch the backup will be stored
    includeFolders = [] # folders to publish
    # includeFolders = [ # SAMPLE
    #     {
    #         "folder": "testFolder", # Folder to include. Do not provide this for source root folder
    #         "recursive": True, # Process folder recursively? Default is False
    #         "includeExtensions": ["py"], # extensions to be included. Do not provide this for all files in Folder
    #         "excludeExtensions": ["pyc"], # extensions to be excluded. Do not provide this if dont needed
    #         "clearExtensions": ["pyc"], # extensions to be deleted from destination. Do not provide this if dont needed
    #         "includeFiles": ["somespecificfile.py"], # files to be specificly included. Do not provide this if dont needed
    #         "excludeFiles": ["somespecificfile.py"], # files to be specificly excluded. Do not provide this if dont needed
    #         "clearFiles": ["somespecificfile.py"], # files to be specificly deleted from destination. Do not provide this if dont needed
    #         "renameFiles": {"somefilenamefromtorename.py": "somewithdifferentname.py"}
    #     }
    # ]
    configFilesJson = [] # config files of type Json to be processed

    configFilesXML = [] # config files of type XML to be processed
    # configFilesXML = [ # SAMPLE
    #     {
    #         "file": "Web.config", # relative path in destination
    #         "changes": [ # List of changes to be made
    #             {
    #                 "xpath": '/Test/Level1/Level2/Level3', # xpath to tag to be changed (first found will be processed)
    #                 "atribute": "someatribute", # Atribute to be updated. Do not provide this if tag text is to be updated
    #                 "value": "value to be writen" # value to be writen
    #             }
    #         ]
    #     }
    # ]
    replacementMap = {}
    # replacementMap = { # SAMPLE
    #     'test.json': {
    #         '[find sting to replace]': 'replacement value'
    #     }
    # }
class PublisherHealper(object):
    """Class for easing the Rar file operations"""

    def _init_(self):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
        """

    def Deply(self, config):
        """Does the dployment

        Args:
            self: The reserved object 'self'
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        print u'... start publish for {}'.format(config.moduleName)

        destination_dir = config.destinationDir
        if not os.path.exists(destination_dir):
            raise AttributeError(u'destination folder {} not found'.format(destination_dir))

        if hasattr(config, "doBackup"):
            if config.doBackup:
                self.__create_backup(config)

        for folder in config.includeFolders:
            self.__do_deploy(folder, config)

        self.__do_process_xml(config)
        self.__do_process_json(config)
        self.__do_string_repalce(config)

    def __create_backup(self, config):
        """Does the backup creation

        Args:
            self: The reserved object 'self'
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        backup_dir = config.backupFolder
        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)
            print u'... created backup folder {}'.format(backup_dir)

        backup_file_name = os.path.join(backup_dir, "{}_{}.zip".format(config.moduleName, _now_for_file()))
        ZipHelper.ZipHelper().CompressDir(config.destinationDir, backup_file_name)
        print u'... backup created!'

    def __do_deploy(self, folder, config):
        """Does the backup creation

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        self.__clear(folder, config)
        files_to_copy = self.__files_to_copy(folder, config)
        self.__do_copy_files_to_dest(folder, files_to_copy, config)

    def __clear(self, folder, config):
        """Clears unnececery files

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        if folder.has_key("clearExtensions") or folder.has_key("clearFiles"):
            clear_extensions = folder[u'clearExtensions'] if folder.has_key("clearExtensions") else []
            clear_files = folder[u'clearFiles'] if folder.has_key("clearFiles") else []
            recursive = folder[u'recursive'] if folder.has_key("recursive") else False

            source_dir = os.path.join(config.sourceDir, folder["folder"]) if folder.has_key("folder") else config.sourceDir
            destination_dir = os.path.join(config.destinationDir, folder["folder"]) if folder.has_key("folder") else config.destinationDir

            if not recursive:
                include_folders = []
            else:
                include_folders = _find_all_folders(destination_dir)
            include_folders.append(destination_dir)

            files_to_delete = []
            for infolder in include_folders:
                for ext in clear_extensions:
                    destination_folder = infolder.replace(source_dir, destination_dir)
                    if not os.path.exists(destination_folder):
                        os.mkdir(destination_folder)
                        print u'... output folder created {}'.format(destination_folder)
                    found_files = _find_file(os.path.join(destination_dir, infolder), ext)
                    if found_files:
                        files_to_delete = files_to_delete + found_files
                for file_to_clear in clear_files:
                    file_name = os.path.join(destination_dir, infolder, file_to_clear)
                    if os.path.exists(file_name):
                        files_to_delete.append(file_name)

            for file_to_delate in files_to_delete:
                os.remove(file_to_delate)
                print u'... file deleted      {}'.format(file_to_delate)

    def __files_to_copy(self, folder, config):
        """Finds files to be copyed

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        recursive = folder[u'recursive'] if folder.has_key("recursive") else False

        source_dir = os.path.join(config.sourceDir, folder["folder"]) if folder.has_key("folder") else config.sourceDir
        destination_dir = os.path.join(config.destinationDir, folder["folder"]) if folder.has_key("folder") else config.destinationDir

        if not recursive:
            include_folders = []
        else:
            include_folders = _find_all_folders(source_dir)
        include_folders.append(source_dir)

        files_to_copy = []
        if folder.has_key("includeExtensions") or folder.has_key("includeFiles"):
            files_to_copy = self.__find_files_to_include(folder, include_folders, source_dir, destination_dir)
        else:
            files_to_copy = self.__find_all_files_to_include(folder, include_folders, source_dir, destination_dir)

        if folder.has_key("excludeExtensions") or folder.has_key("excludeFiles"):
            files_to_copy = self.__exclude_files(folder, files_to_copy)

        return files_to_copy

    def __find_files_to_include(self, folder, include_folders, source_dir, destination_dir):
        files_to_copy = []
        include_extensions = folder[u'includeExtensions'] if folder.has_key("includeExtensions") else []
        include_files = folder[u'includeFiles'] if folder.has_key("includeFiles") else []

        for infolder in include_folders:
            for ext in include_extensions:
                found_files = _find_file(infolder, ext)
                if found_files:
                    files_to_copy = files_to_copy + found_files
                    if not infolder == source_dir:
                        destination_folder = infolder.replace(source_dir, destination_dir)
                        if not os.path.exists(destination_folder):
                            os.mkdir(destination_folder)
                            print u'... output folder created {}'.format(destination_folder)
            for file_name in include_files:
                found_files = _find_file_by_name(infolder, file_name)
                if found_files:
                    files_to_copy = files_to_copy + found_files
                    if not infolder == source_dir:
                        destination_folder = infolder.replace(source_dir, destination_dir)
                        if not os.path.exists(destination_folder):
                            os.mkdir(destination_folder)
                            print u'... output folder created {}'.format(destination_folder)
        return files_to_copy

    def __find_all_files_to_include(self, folder, include_folders, source_dir, destination_dir):
        files_to_copy = []
        for infolder in include_folders:
            found_files = _find_all_files(os.path.join(source_dir, infolder))
            if found_files:
                files_to_copy = files_to_copy + found_files
                if not folder == source_dir:
                    destination_folder = os.path.join(destination_dir, os.path.basename(infolder))
                    if not os.path.exists(destination_folder):
                        os.mkdir(destination_folder)
                        print u'... output folder created {}'.format(destination_folder)
        return files_to_copy

    def __exclude_files(self, folder, files_to_copy):
        exclude_extensions = folder[u'excludeExtensions'] if folder.has_key("excludeExtensions") else []
        exclude_files = folder[u'excludeFiles'] if folder.has_key("excludeFiles") else []

        for ext in exclude_extensions:
            files_to_copy = list(fn for fn in files_to_copy if not os.path.basename(fn).lower().endswith('.' + (ext.lower())))

        for exclude_file in exclude_files:
            files_to_copy = list(fn for fn in files_to_copy if not os.path.basename(fn).lower() == exclude_file.lower())
        return files_to_copy

    def __do_copy_files_to_dest(self, folder, files_to_copy, config):
        """Finds files to be copyed

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            files_to_copy ([list]): path of files to be copyed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        source_dir = os.path.join(config.sourceDir, folder["folder"]) if folder.has_key("folder") else config.sourceDir
        destination_dir = os.path.join(config.destinationDir, folder["folder"]) if folder.has_key("folder") else config.destinationDir

        for copy_file in files_to_copy:
            dest_file = copy_file
            dest_file = dest_file.replace(source_dir, destination_dir)
            dest_file = self.__rename_file_if_needed(dest_file, folder)
            replaced = False
            thesame = False

            if os.path.exists(dest_file):
                copy_hash = _md5(copy_file)
                dest_hash = _md5(dest_file)
                if copy_hash <> dest_hash:
                    os.remove(dest_file)
                    replaced = True
                else:
                    thesame = True
            if not thesame:
                shutil.copy2(copy_file, dest_file)
                if not replaced:
                    print u'... file copy    {}'.format(dest_file)
                else:
                    print u'... file replace {}'.format(dest_file)

    def __rename_file_if_needed(self, dest_file, folder):
        rename_files = folder[u'renameFiles'] if folder.has_key("renameFiles") else {}
        dir_name, file_name = os.path.split(dest_file)
        for rename_file in rename_files:
            if file_name.upper() == rename_file.upper():
                return os.path.join(dir_name, rename_files[rename_file])
        return dest_file

    def __do_process_xml(self, config):
        """Changes required values in config xml

        Args:
            self: The reserved object 'self'
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        for config_file in config.configFilesXML:
            params_helper = xmlParamsHealper.XMLParams(None, None, os.path.join(config.destinationDir, config_file['file']))
            params_helper.GetParams()
            for change in config_file['changes']:
                is_string = False
                do_append = False
                if change.has_key('string'):
                    if change['string']:
                        is_string = True
                if change.has_key('append'):
                    if change['append']:
                        do_append = True
                if do_append:
                    attribute = None
                    key = None
                    if change.has_key("atribute"):
                        attribute = change['atribute']
                    if change.has_key("appendKey"):
                        key = change['appendKey']
                    params_helper.AppendValueByPath(change['xpath'], key, change['value'], attribute, isString=is_string)
                else:
                    if change.has_key("atribute"):
                        params_helper.UpdateAtributeByPath(change['xpath'], change['atribute'], change['value'])
                    else:
                        params_helper.UpdateValueByPath(change['xpath'], change['value'])
            params_helper.WriteParams()
            print u'... config file {} updated'.format(config_file['file'])

    def __do_process_json(self, config):
        """Changes required values in config xml

        Args:
            self: The reserved object 'self'
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        for config_file in config.configFilesJson:
            params_helper = JsonParamsHelper.JsonParams(None, None, os.path.join(config.destinationDir, config_file['file']))
            params_helper.GetParams()
            for change in config_file['changes']:
                is_json = False
                do_append = False
                if change.has_key('json'):
                    if change['json']:
                        is_json = True
                if change.has_key('append'):
                    if change['append']:
                        do_append = True
                if do_append:
                    params_helper.AppendValueByPath(change['xpath'], change['appendKey'], change['value'], is_json)
                else:
                    params_helper.UpdateValueByPath(change['xpath'], change['value'], is_json)
            params_helper.WriteParams(False)
            print u'... config file {} updated'.format(config_file['file'])

    def __do_string_repalce(self, config):
        """Replace required values by sring replacement

        Args:
            self: The reserved object 'self'
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        for file_name in config.replacementMap:
            replacement_map = config.replacementMap[file_name]
            path = os.path.join(config.destinationDir, file_name)
            _replace_in_file(path, replacement_map)
            print u'... file {} replaced strings'.format(path)

def _replace_in_file(path, replace_map):
    """replaces values in files using replace_map
    """
    with codecs.open(path, 'r') as f:
        newlines = []
        for line in f.readlines():
            for key, value in replace_map.items():
                line = line.replace(key, value)
            newlines.append(line)
    with open(path, 'w') as f:
        for line in newlines:
            f.write(line)

def _find_all_files(directory):
    """Finds files in the directory

    Args:
        dir: The directory in which to look for the file
    """
    found_files = [directory + "\\" + fn
                   for fn in os.listdir(directory)]
    found_files.sort()
    return found_files

def _find_file(directory, ext):
    """Finds files in the directory

    Args:
        Dir: The directory in which to look for the file
        Ext: The extension to search for
    """
    found_files = [directory + "\\" + fn
                   for fn in os.listdir(directory) if fn.lower().endswith('.' + (ext.lower()))]
    found_files.sort()
    return found_files

def _find_file_by_name(directory, file_name):
    """Finds files in the directory

    Args:
        Dir: The directory in which to look for the file
        fileName: File name to search for
    """
    found_files = [directory + "\\" + fn
                   for fn in os.listdir(directory) if fn.lower() == file_name.lower()]
    found_files.sort()
    return found_files

def _find_all_folders(directory):
    """Finds files in the directory

    Args:
        Dir: The directory in which to look for the file
        Ext: The extension to search for
    """
    return [x[0] for x in os.walk(directory)]

def _md5(filename):
    """calculates file md5 cheksumm

    Args:
        fname ([string]): File path

    Returns:
        [string]: hex digest
    """
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as opened_file:
        for chunk in iter(lambda: opened_file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def _now_for_file():
    """returns date now formated for filename

    Returns:
        [string]: [date reprezentation as string]
    """
    return datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")
