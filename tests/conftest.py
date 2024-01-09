from unittest.mock import Mock

import pytest
from pyairtable.api.api import Api as AirtableApi
from pyairtable.api.base import Base as AirtableBase

from .dummy_returns import BASE_SCHEMA, DUMMY_RECORDS, GET_API_BASES


@pytest.fixture(name="_mock_api")
def mock_api(mocker):
    mock = Mock(spec=AirtableApi)
    mock.base.return_value.table.return_value.iterate.return_value = DUMMY_RECORDS

    mocker.patch("airtable_to_sqlite.main.AirtableApi", return_value=mock)
    return mock


@pytest.fixture(name="_mock_base")
def mock_base(mocker):
    mock = Mock(spec=AirtableBase)
    mock.table.return_value.iterate.return_value = DUMMY_RECORDS

    mocker.patch("airtable_to_sqlite.schema.AirtableBase", return_value=mock)
    return mock


@pytest.fixture(name="_mock_get_api_bases")
def mock_get_api_bases(mocker):
    mocker.patch("pyairtable.metadata.get_api_bases", return_value=GET_API_BASES)


@pytest.fixture(name="_mock_base_schema")
def mock_base_schema(mocker):
    mocker.patch("pyairtable.metadata.get_base_schema", return_value=BASE_SCHEMA)
