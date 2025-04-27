#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import contextlib
import csv
import errno
import pandas
from typing import Dict, List, TextIO

import paramiko
import smart_open


@contextlib.contextmanager
def sftp_client(
    host: str,
    port: int,
    username: str,
    password: str,
) -> paramiko.SFTPClient:
    with paramiko.SSHClient() as client:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            host,
            port,
            username=username,
            password=password,
            look_for_keys=False,
        )
        sftp = client.open_sftp()
        yield sftp


class SftpClient:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        destination_path: str = "",
        port: int = 22,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.destination_path = destination_path
        self._df: Dict[str, pandas.DataFrame] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get_path(self, stream: str) -> str:
        if type(self.destination_path) is str:
            if len(self.destination_path) > 0:
                return f"{self.destination_path}/airbyte_csv_{stream}.csv"
            else:
                return f"airbyte_csv_{stream}.csv"
        else:
            return f"airbyte_csv_{stream}.csv"

    def _get_uri(self, stream: str) -> str:
        path = self._get_path(stream)
        return f"sftp://{self.username}:{self.password}@{self.host}:{self.port}/{path}"

    def _open(self, stream: str) -> TextIO:
        uri = self._get_uri(stream)
        return smart_open.open(uri, mode="w+")

    def close(self):
        """
        Do not use 
        """
        pass 

    def write(self, stream: str, record: Dict) -> None:
        """
        Append stream record into dataframe
        :param stream: source stream to write
        :type stream: str
        :param record: record to register into dataframe
        :type record: dict 
        """
        if stream not in self._df:
            self._df[stream] = pandas.DataFrame.from_records(record)
        else: 
            self._df[stream] = pandas.concat([self._df[stream], pandas.DataFrame.from_records(record)])
    
    def flush(self, stream: str) -> None:
        """
        Flush stream to ftp file server and clean memeory use afterward.
        :param stream: file to create on remote ftp server 
        :type stream: str
        """
        content = self._df[stream].to_csv(header=True, index=False, doublequote=True, encoding="utf-8",sep=',', lineterminator='\n', quoting=csv.QUOTE_ALL).removesuffix('\n')
        fd = self._open(stream)
        fd.write(content)
        fd.close()
        del self._df[stream]


    def flush_all(self) -> None:
        """
        Flush all stream to ftp file server
        """
        for stream in self._df.keys():
            self.flush(stream)

    def delete(self, stream: str) -> None:
        """
        Delete file on remote ftp sile server
        """
        with sftp_client(self.host, self.port, self.username, self.password) as sftp:
            try:
                path = self._get_path(stream)
                sftp.remove(path)
            except IOError as err:
                # Ignore the case where the file doesn't exist, only raise the
                # exception if it's something else
                if err.errno != errno.ENOENT:
                    raise
