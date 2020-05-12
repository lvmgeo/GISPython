# -*- coding: utf-8 -*-
"""
    SFTP operations module
"""

import paramiko

class SFTPHelper:
    """Class for easing the SFTP operations"""

    def __init__(self, userName, password, host, port, pkey_file = None):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            username: Username
            password: Password (provide None if using pkey_file parameter)
            host: IP adress
            port: Port number
            pkey_file: path to rsa private key file
        """
        self.host = host
        self.port = port
        self.username = userName
        self.password = password

        if not pkey_file is None:
            pkey = paramiko.RSAKey.from_private_key_file(pkey_file)

        # Transporta objekta izveide
        self.transport = paramiko.Transport((self.host, self.port))
        if pkey_file is None:
            self.transport.connect(username=self.username, password=self.password)
        else:
            self.transport.connect(username=self.username, pkey = pkey)

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
