from airtable_to_sqlite.constants import PreferedNamingMethod
from airtable_to_sqlite.schema import BaseRecord, FieldSchema, TableSchema, ViewSchema


def test_fieldschema_dbname():
    f = FieldSchema(id="fld123", name="Name", type="text")
    assert f.db_name(PreferedNamingMethod.ID) == "fld123"
    assert f.db_name(PreferedNamingMethod.NAME) == "Name"
    assert f.db_name() == "Name"


def test_fieldschema_column_type():
    assert FieldSchema(id="fld123", name="Name", type="text").column_type == str
    assert FieldSchema(id="fld123", name="Name", type="number").column_type == float
    assert FieldSchema(id="fld123", name="Name", type="multipleRecordLinks").column_type is None
    assert FieldSchema(id="fld123", name="Name", type="checkbox").column_type == bool
    assert FieldSchema(id="fld123", name="Name", type="formula").column_type == str
    assert (
        FieldSchema(id="fld123", name="Name", type="formula", options={"result": {"type": "number"}}).column_type
        == float
    )
    assert (
        FieldSchema(id="fld123", name="Name", type="formula", options={"result": {"type": "text"}}).column_type == str
    )
    assert (
        FieldSchema(id="fld123", name="Name", type="formula", options={"result": {"type": "checkbox"}}).column_type
        == bool
    )


def test_fieldschema_choices():
    assert FieldSchema(id="fld123", name="Name", type="text").choices is None
    assert FieldSchema(id="fld123", name="Name", type="number").choices is None
    assert FieldSchema(id="fld123", name="Name", type="multipleRecordLinks").choices is None

    assert FieldSchema(id="fld123", name="Name", type="text", options={"choices": []}).choices == []
    assert FieldSchema(
        id="fld123",
        name="Name",
        type="text",
        options={
            "choices": [
                {
                    "id": "opt123",
                    "name": "Option 1",
                    "color": "red",
                }
            ]
        },
    ).choices == [
        {
            "id": "opt123",
            "name": "Option 1",
            "color": "red",
            "fieldId": "fld123",
        }
    ]
    assert FieldSchema(id="fld123", name="Name", type="text", options={}).choices == []


def test_fieldschema_for_insertion():
    f = FieldSchema(id="fld123", name="Name", type="text")
    t = TableSchema(id="tbl123", name="Table", fields=[f], views=[], primaryFieldId="fld123")
    assert f.for_insertion(t) == {
        "id": "fld123",
        "name": "Name",
        "type": "text",
        "tableId": "tbl123",
        "options": None,
        "linkedTableId": None,
        "isReversed": None,
        "prefersSingleRecordLink": None,
        "inverseLinkFieldId": None,
        "isValid": None,
        "recordLinkFieldId": None,
        "icon": None,
        "color": None,
        "referencedFieldIds": None,
        "result": None,
        "precision": None,
        "symbol": None,
    }


def test_fieldschema_for_insertion_options():
    f = FieldSchema(id="fld123", name="Name", type="text", options={"precision": 4})
    t = TableSchema(id="tbl123", name="Table", fields=[f], views=[], primaryFieldId="fld123")
    assert f.for_insertion(t) == {
        "id": "fld123",
        "name": "Name",
        "type": "text",
        "tableId": "tbl123",
        "options": {},
        "linkedTableId": None,
        "isReversed": None,
        "prefersSingleRecordLink": None,
        "inverseLinkFieldId": None,
        "isValid": None,
        "recordLinkFieldId": None,
        "icon": None,
        "color": None,
        "referencedFieldIds": None,
        "result": None,
        "precision": 4,
        "symbol": None,
    }


def test_fieldschema_for_insertion_options_unknown():
    f = FieldSchema(id="fld123", name="Name", type="text", options={"precision": 4, "flurb": "blurb"})
    t = TableSchema(id="tbl123", name="Table", fields=[f], views=[], primaryFieldId="fld123")
    assert f.for_insertion(t) == {
        "id": "fld123",
        "name": "Name",
        "type": "text",
        "tableId": "tbl123",
        "options": {"flurb": "blurb"},
        "linkedTableId": None,
        "isReversed": None,
        "prefersSingleRecordLink": None,
        "inverseLinkFieldId": None,
        "isValid": None,
        "recordLinkFieldId": None,
        "icon": None,
        "color": None,
        "referencedFieldIds": None,
        "result": None,
        "precision": 4,
        "symbol": None,
    }


def test_tableschema_dbname():
    f = TableSchema(id="tbl123", name="Table", fields=[], views=[], primaryFieldId="fld123")
    assert f.db_name(PreferedNamingMethod.ID) == "tbl123"
    assert f.db_name(PreferedNamingMethod.NAME) == "Table"
    assert f.db_name() == "Table"


def test_viewschema_dbname():
    f = ViewSchema(id="vew123", name="View", type="View")
    assert f.db_name(PreferedNamingMethod.ID) == "vew123"
    assert f.db_name(PreferedNamingMethod.NAME) == "View"
    assert f.db_name() == "View"


def test_tableschema_get_table_data(_mock_api):
    t = TableSchema(id="tbl123", name="Table", fields=[], views=[], primaryFieldId="fld123")

    table_data = list(t.get_table_data(_mock_api))
    assert len(table_data) == 4
    assert table_data[0] == {
        "id": "rec123",
        "createdTime": "2021-01-01T00:00:00.000Z",
        "fields": {
            "Name": "Test 3",
            "Number": 123,
            "Checkbox": True,
        },
    }


def test_baserecord():
    b = BaseRecord(
        id="app123",
        name="Base",
        permissionLevel="create",
    )
    assert b.id == "app123"
