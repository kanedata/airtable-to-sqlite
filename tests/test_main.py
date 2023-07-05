import pytest
from sqlite_utils import Database
from sqlite_utils.db import Table

from airtable_to_sqlite.constants import (
    AirtablePersonalAccessToken,
    PreferedNamingMethod,
)
from airtable_to_sqlite.main import AirtableBaseToSqlite, get_base_records
from airtable_to_sqlite.schema import BaseRecord


def test_airtable_base_to_sqlite_get_schema(_mock_base_schema):
    db = Database(memory=True)
    base = BaseRecord(id="app123", name="My Base", permissionLevel="create")
    api = AirtableBaseToSqlite(
        personal_access_token=AirtablePersonalAccessToken("key123"),
        db=db,
        base=base,
        prefer_ids=PreferedNamingMethod.ID,
    )
    api.get_schema()
    assert len(api.table_meta) == 2
    assert api.table_meta[0].id == "tbl123"


def test_airtable_base_to_sqlite_create_metadata_tables():
    db = Database(memory=True)
    base = BaseRecord(id="app123", name="My Base", permissionLevel="create")
    api = AirtableBaseToSqlite(
        personal_access_token=AirtablePersonalAccessToken("key123"),
        db=db,
        base=base,
        prefer_ids=PreferedNamingMethod.ID,
    )
    api.create_metadata_tables()
    assert len(api.meta_tables) == 5
    assert len(api.meta_tables["_meta_field_choice"].columns) == 4


def test_airtable_base_to_sqlite_create_all_table_metadata(_mock_base_schema):
    db = Database(memory=True)
    base = BaseRecord(id="app123", name="My Base", permissionLevel="create")

    api = AirtableBaseToSqlite(
        personal_access_token=AirtablePersonalAccessToken("key123"),
        db=db,
        base=base,
        prefer_ids=PreferedNamingMethod.ID,
    )
    api.get_schema()
    api.create_metadata_tables()
    api.create_all_table_metadata()
    assert len(api.foreign_keys) > 0
    api.create_foreign_keys()

    assert "tbl123" in db.table_names()

    columns = [c.name for c in db["tbl123"].columns]
    pks = [c.name for c in db["tbl123"].columns if c.is_pk]

    assert "_id" in columns
    assert "_createdTime" in columns
    assert pks == ["_id"]
    assert len(columns) == 5
    assert "fld123456789C" in columns

    # test foreign keys have been created
    assert len(api.foreign_keys) == 0
    meta_table = db["_meta_table"]
    assert isinstance(meta_table, Table)
    assert len(meta_table.foreign_keys) == 1


def test_airtable_base_to_sqlite_create_all_table_metadata_prefer_name(_mock_base_schema):
    db = Database(memory=True)
    base = BaseRecord(id="app123", name="My Base", permissionLevel="create")
    api = AirtableBaseToSqlite(
        personal_access_token=AirtablePersonalAccessToken("key123"),
        db=db,
        base=base,
        prefer_ids=PreferedNamingMethod.NAME,
    )
    api.get_schema()
    api.create_metadata_tables()
    api.create_all_table_metadata()
    api.create_foreign_keys()

    assert "My Table" in db.table_names()

    columns = [c.name for c in db["My Table"].columns]
    pks = [c.name for c in db["My Table"].columns if c.is_pk]

    assert "_id" in columns
    assert "_createdTime" in columns
    assert pks == ["_id"]
    assert len(columns) == 5
    assert "IP Address" in columns


def test_airtable_base_to_sqlite_insert_settings(_mock_base_schema):
    db = Database(memory=True)
    base = BaseRecord(id="app123", name="My Base", permissionLevel="create")
    api = AirtableBaseToSqlite(
        personal_access_token=AirtablePersonalAccessToken("key123"),
        db=db,
        base=base,
        prefer_ids=PreferedNamingMethod.NAME,
    )
    api.get_schema()
    api.create_metadata_tables()
    api.create_all_table_metadata()
    api.create_foreign_keys()
    api.insert_settings()

    assert "_meta_settings" in db.table_names()

    data = list(db["_meta_settings"].rows)

    assert len(data) == 4


def test_airtable_base_to_sqlite_run(_mock_base_schema, _mock_api):
    db = Database(memory=True)
    base = BaseRecord(id="app123", name="My Base", permissionLevel="create")
    api = AirtableBaseToSqlite(
        personal_access_token=AirtablePersonalAccessToken("key123"),
        db=db,
        base=base,
        prefer_ids=PreferedNamingMethod.NAME,
    )
    api.run()

    assert "_meta_settings" in db.table_names()

    data = list(db["_meta_settings"].rows)

    assert len(data) == 4


def test_get_base_records_all(_mock_get_api_bases):
    bases = list(get_base_records(personal_access_token=AirtablePersonalAccessToken("key123")))
    assert len(bases) == 2


def test_get_base_records_single(_mock_get_api_bases):
    bases = list(get_base_records(personal_access_token=AirtablePersonalAccessToken("key123"), base_ids=["app123"]))
    assert len(bases) == 1


def test_get_base_records_missing(_mock_get_api_bases):
    with pytest.raises(KeyError):
        list(
            get_base_records(personal_access_token=AirtablePersonalAccessToken("key123"), base_ids=["app123", "app456"])
        )
    with pytest.raises(KeyError):
        list(get_base_records(personal_access_token=AirtablePersonalAccessToken("key123"), base_ids=["app456"]))
