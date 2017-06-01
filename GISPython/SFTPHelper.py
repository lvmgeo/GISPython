# -*- coding: utf-8 -*-
"""
    SFTP operations module
"""

import paramiko

class SFTPHelper:
    """Class for easing the SFTP operations"""

    def __init__(self, userName, password, host, port):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            username: Username
            password: Password
            host: IP adress
            port: Port number
        """
        self.host = host
        self.port = port
        self.username = userName
        self.password = password

        # Transporta objekta izveide
        self.transport = paramiko.Transport((self.host, self.port))
        self.transport.connect(username=self.username, password=self.password)

        # SFTP objekta izveide
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def upload(self, local, remote):
        """Upload the file, using SFTP

        Args:
            self: The reserved object 'self'
            local: Uploadable file local path
            remote: Uploadable file path on the server
        """
        self.sftp.put(local, remote)

    def download(self, remote, local):
        """Download the file, using SFTP

        Args:
            self: The reserved object 'self'
            remote: Downloadable file path on the server
            local: Local download path
        """
        self.sftp.get(remote, local)

    def close(self):
        """Closes the connection, if it is active"""
        if self.transport.is_active():
            self.sftp.close()
            self.transport.close()
