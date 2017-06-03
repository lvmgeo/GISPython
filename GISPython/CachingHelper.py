# -*- coding: utf-8 -*-
"""
    Carries out service caching on ArcServer providing x3 retry capabilities
"""

#Modula pamata klase
class CachingHelper:
    """Support class which generates the caches"""
    def __init__(self, Tool, vServer, vExtent="#", vTerritoryLayer="#"):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            Tool: GEOPython tool
            vServer: Server
            vExtent: Extent
            vTerritoryLayer: Territory layer
        """
        self.Tool = Tool
        self.Server = vServer
        self.Extent = vExtent
        self.TerritoryLayer = vTerritoryLayer

    def GenerateCache(self, vService, vInstances, vCashScales, vFolder="#", vDeleteScales='#'):
        """Base procedure of the tool

        Args:
            self: The reserved object 'self'
            vService: Cacheable serviss
            vInstances: Cacheable instance count
            vCashScales: Cacheable scales
            vFolder: Cache service directory
            vDeleteScales: Scales to delete
        """

        if vFolder == "#":
            vFolder = ""
        elif vFolder == None:
            vFolder = ""
        else:
            vFolder = str(vFolder) + "\\"
        vFolder = "\\" +  vFolder

        if vDeleteScales == '#':
            vDeleteScales = vCashScales

        input_service = self.Server + vFolder + str(vService) + '.MapServer'
        if vDeleteScales != "None":
            try: # 1 try to delete
                self.Tool.gp.ManageMapServerCacheTiles_server(input_service, vCashScales, "DELETE_TILES", vInstances, self.TerritoryLayer, self.Extent, 'WAIT')
                self.Tool.OutputMessages()
            except: # 2 try to delete
                self.Tool.OutputMessages()
                self.Tool.AddMessage("Delete Restart x1 ----------------------------------------------- " + self.Tool.MyNow())
                try:
                    self.Tool.gp.ManageMapServerCacheTiles_server(input_service, vCashScales, "DELETE_TILES", vInstances, self.TerritoryLayer, self.Extent, 'WAIT')
                    self.Tool.OutputMessages()
                except: # 3 try to delete
                    self.Tool.OutputMessages()
                    self.Tool.AddMessage("Delete Restart x2 ----------------------------------------------- " + self.Tool.MyNow())
                    try:
                        self.Tool.gp.ManageMapServerCacheTiles_server(input_service, vCashScales, "DELETE_TILES", vInstances, self.TerritoryLayer, self.Extent, 'WAIT')
                        self.Tool.OutputMessages()
                    except:
                        self.Tool.OutputMessages()
                        self.Tool.AddWarning("Delete Restart x3 for service {0} - Failed ------------------------------------- {1} ".format(input_service, self.Tool.MyNow()))

        try: # 1 try
            self.Tool.gp.ManageMapServerCacheTiles_server(input_service, vCashScales, "RECREATE_ALL_TILES", vInstances, self.TerritoryLayer, self.Extent, 'WAIT')
            self.Tool.OutputMessages()
        except: # 2 try
            self.Tool.OutputMessages()
            self.Tool.AddMessage("Restart x1 ----------------------------------------------- " + self.Tool.MyNow())
            try: 
                self.Tool.gp.ManageMapServerCacheTiles_server(input_service, vCashScales, "RECREATE_EMPTY_TILES", vInstances, self.TerritoryLayer, self.Extent, 'WAIT')
                self.Tool.OutputMessages()
            except: # 3 try
                self.Tool.OutputMessages()
                self.Tool.AddMessage("Restart x2 ----------------------------------------------- " + self.Tool.MyNow())
                try:
                    self.Tool.gp.ManageMapServerCacheTiles_server(input_service, vCashScales, "RECREATE_EMPTY_TILES", vInstances, self.TerritoryLayer, self.Extent, 'WAIT')
                    self.Tool.OutputMessages()
                except:
                    self.Tool.OutputMessages()
                    self.Tool.AddWarning("Caching Restart x3 for service {0} - Failed ------------------------------------- {1} ".format(input_service, self.Tool.MyNow()))
