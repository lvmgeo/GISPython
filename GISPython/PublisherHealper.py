# -*- coding: utf-8 -*-
"""
     Deployment publishing operations module
"""

import sys, os, shutil, hashlib, datetime
import ZipHelper
import xmlParamsHealper

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
    #         "clearFiles": ["somespecificfile.py"] # files to be specificly deleted from destination. Do not provide this if dont needed
    #     }
    # ]
    # configFilesJson = [] # config files of type Json to be processed # !!! not implemented
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



class PublisherHealper:
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

        destinationDir = config.destinationDir
        if not os.path.exists(destinationDir):
            raise AttributeError(u'destination folder {} not found'.format(destinationDir))

        if hasattr(config, "doBackup"):
            if config.doBackup == True:
                self._createBackup(config)

        for folder in config.includeFolders:
            self._doDeploy(folder, config)

        self._doProcessXML(config)

    def _createBackup(self, config):
        """Does the backup creation

        Args:
            self: The reserved object 'self'
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        backupDir = config.backupFolder
        if not os.path.exists(backupDir):
            os.mkdir(backupDir)
            print u'... created backup folder {}'.format(backupDir)

        ZipHelper.ZipHelper().CompressDir(config.destinationDir, os.path.join(backupDir, "{}_{}.zip".format(config.moduleName, _MyNowFileSafe())))
        print u'... backup created!'

    def _doDeploy(self, folder, config):
        """Does the backup creation

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        self._clear(folder, config)
        filesToCopy = self._filesToCopy(folder, config)
        self._doCopyFilesToDest(folder, filesToCopy, config)

    def _clear(self, folder, config):
        """Clears unnececery files

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        if folder.has_key("clearExtensions") or folder.has_key("clearFiles"):
            clearExtensions = folder[u'clearExtensions'] if folder.has_key("clearExtensions") else []
            clearFiles = folder[u'clearFiles'] if folder.has_key("clearFiles") else []
            recursive = folder[u'recursive'] if folder.has_key("recursive") else False

            sourceDir = os.path.join(config.sourceDir, folder["folder"]) if folder.has_key("folder") else config.sourceDir
            destinationDir = os.path.join(config.destinationDir, folder["folder"]) if folder.has_key("folder") else config.destinationDir

            if not recursive:
                includeFolders = []
            else:
                includeFolders = _FindAllFolders(destinationDir)
            includeFolders.append(destinationDir)

            filesToDelete = []
            for infolder in includeFolders:
                for ext in clearExtensions:
                    destinationFolder = infolder.replace(sourceDir, destinationDir)
                    if not os.path.exists(destinationFolder):
                        os.mkdir(destinationFolder)
                        print u'... output folder created {}'.format(destinationFolder)
                    foundFiles = _FindFile(os.path.join(destinationDir, infolder), ext)
                    if len(foundFiles)>0:
                        filesToDelete = filesToDelete + foundFiles
                for cFile in clearFiles:
                    fName = os.path.join(destinationDir, infolder, cFile)
                    if os.path.exists(fName):
                        filesToDelete.append(fName)

            for delFile in filesToDelete:
                os.remove(delFile)
                print u'... file deleted      {}'.format(delFile)

    def _filesToCopy(self, folder, config):
        """Finds files to be copyed

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        recursive = folder[u'recursive'] if folder.has_key("recursive") else False

        sourceDir = os.path.join(config.sourceDir, folder["folder"]) if folder.has_key("folder") else config.sourceDir
        destinationDir = os.path.join(config.destinationDir, folder["folder"]) if folder.has_key("folder") else config.destinationDir

        if not recursive:
            includeFolders = []
        else:
            includeFolders = _FindAllFolders(sourceDir)
        includeFolders.append(sourceDir)

        filesToCopy = []
        if folder.has_key("includeExtensions") or folder.has_key("includeFiles"):
            includeExtensions = folder[u'includeExtensions'] if folder.has_key("includeExtensions") else []
            includeFiles = folder[u'includeFiles'] if folder.has_key("includeFiles") else []

            for infolder in includeFolders:
                for ext in includeExtensions:
                    foundFiles = _FindFile(infolder, ext)
                    if len(foundFiles)>0:
                        filesToCopy = filesToCopy + foundFiles
                        if not infolder == sourceDir:
                            destinationFolder = infolder.replace(sourceDir, destinationDir)
                            if not os.path.exists(destinationFolder):
                                os.mkdir(destinationFolder)
                                print u'... output folder created {}'.format(destinationFolder)
                for fileName in includeFiles:
                    foundFiles = _FindFileByName(infolder, fileName)
                    if len(foundFiles)>0:
                        filesToCopy = filesToCopy + foundFiles
                        if not infolder == sourceDir:
                            destinationFolder = infolder.replace(sourceDir, destinationDir)
                            if not os.path.exists(destinationFolder):
                                os.mkdir(destinationFolder)
                                print u'... output folder created {}'.format(destinationFolder)
        else:
            for infolder in includeFolders:
                foundFiles = _FindAllFiles(os.path.join(sourceDir, infolder))
                if len(foundFiles)>0:
                    filesToCopy = filesToCopy + foundFiles
                    if not folder == sourceDir:
                        destinationFolder = os.path.join(destinationDir, os.path.basename(infolder))
                        if not os.path.exists(destinationFolder):
                            os.mkdir(destinationFolder)
                            print u'... output folder created {}'.format(destinationFolder)
        
        if folder.has_key("excludeExtensions") or folder.has_key("excludeFiles"):
            excludeExtensions = folder[u'excludeExtensions'] if folder.has_key("excludeExtensions") else []
            excludeFiles = folder[u'excludeFiles'] if folder.has_key("excludeFiles") else []

            for ext in excludeExtensions:
                filesToCopy = list(fn for fn in filesToCopy if not os.path.basename(fn).lower().endswith('.' + (ext.lower())))

            for exFile in excludeFiles:
                filesToCopy = list(fn for fn in filesToCopy if not os.path.basename(fn).lower() == exFile.lower())

        return filesToCopy

    def _doCopyFilesToDest(self, folder, filesToCopy, config):
        """Finds files to be copyed

        Args:
            self: The reserved object 'self'
            folder ([string]): relative path to folder to be processed
            filesToCopy ([list]): path of files to be copyed
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        sourceDir = os.path.join(config.sourceDir, folder["folder"]) if folder.has_key("folder") else config.sourceDir
        destinationDir = os.path.join(config.destinationDir, folder["folder"]) if folder.has_key("folder") else config.destinationDir

        for copyFile in filesToCopy:
            destFile = copyFile
            destFile = destFile.replace(sourceDir, destinationDir)
            replaced = False
            thesame = False

            if os.path.exists(destFile):
                copyHash = _md5(copyFile)
                destHash = _md5(destFile)
                if copyHash <> destHash:
                    os.remove(destFile)
                    replaced = True
                else:
                    thesame = True
            if not thesame:
                shutil.copy2(copyFile, destFile)
                if not replaced:
                    print u'... file copy    {}'.format(destFile)
                else:
                    print u'... file replace {}'.format(destFile)

    def _doProcessXML(self, config):
        """Changes required values in config xml

        Args:
            self: The reserved object 'self'
            config ([PublisherHealperConfig]): Configuration of deplyment
        """
        for configFile in config.configFilesXML:
            PH = xmlParamsHealper.XMLParams(None, None, os.path.join(config.destinationDir, configFile['file']))
            PH.GetParams()
            for change in configFile['changes']:
                if change.has_key("atribute"): 
                    PH.UpdateAtributeByPath(change['xpath'], change['atribute'], change['value'])
                else:
                    PH.UpdateValueByPath(change['xpath'], change['value'])
            PH.WriteParams()
            print u'... config file {} updated'.format(configFile['file'])

def _FindAllFiles(Dir):
    """Finds files in the directory

    Args:
        Dir: The directory in which to look for the file
    """
    foundFiles = [Dir + "\\" + fn
                    for fn in os.listdir(Dir)]
    foundFiles.sort()
    return foundFiles

def _FindFile(Dir, Ext):
    """Finds files in the directory

    Args:
        Dir: The directory in which to look for the file
        Ext: The extension to search for
    """
    foundFiles = [Dir + "\\" + fn
                    for fn in os.listdir(Dir) if fn.lower().endswith('.' + (Ext.lower()))]
    foundFiles.sort()
    return foundFiles

def _FindFileByName(Dir, fileName):
    """Finds files in the directory

    Args:
        Dir: The directory in which to look for the file
        fileName: File name to search for
    """
    foundFiles = [Dir + "\\" + fn
                    for fn in os.listdir(Dir) if fn.lower() == fileName.lower()]
    foundFiles.sort()
    return foundFiles

def _FindAllFolders(Dir):
    """Finds files in the directory

    Args:
        Dir: The directory in which to look for the file
        Ext: The extension to search for
    """
    return [x[0] for x in os.walk(Dir)]

def _md5(fname):
    """calculates file md5 cheksumm
    
    Args:
        fname ([string]): File path
    
    Returns:
        [string]: hex digest
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def _MyNowFileSafe():
        """returns date now formated for filename   
        
        Returns:
            [string]: [date reprezentation as string]
        """
        return datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")