#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_sftp_csv.client import SftpClient


@pytest.fixture
def client() -> SftpClient:
    return SftpClient("sample-host", "sample-username", "sample-password", "/sample/path")


def test_get_path(client):
    path = client._get_path("mystream")
    assert path == "/sample/path/airbyte_csv_mystream.csv"


def test_get_uri(client):
    uri = client._get_uri("mystream2")
    assert uri == "sftp://sample-username:sample-password@sample-host:22//sample/path/airbyte_csv_mystream2.csv"
