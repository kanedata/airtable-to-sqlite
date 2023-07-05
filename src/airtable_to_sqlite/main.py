import logging
from collections.abc import Generator
from datetime import datetime
from typing import Optional

import pyairtable.metadata
import sqlite_utils
from pyairtable.api.api import Api as AirtableApi
from pyairtable.api.base import Base as AirtableBase
from sqlite_utils import Database
from tqdm import tqdm

from airtable_to_sqlite.constants import (
    META_TABLES,
    AirtablePersonalAccessToken,
    ForeignKeySet,
    PreferedNamingMethod,
)
from airtable_to_sqlite.schema import BaseRecord, FieldSchema, TableSchema, ViewSchema

logger = logging.getLogger(__name__)


def get_base_records(
    personal_access_token: AirtablePersonalAccessToken, base_ids: Optional[list[str]] = None
) -> Generator[BaseRecord, None, None]:
    logger.info("Fetching base record from Airtable...")
    api = AirtableApi(personal_access_token)
    all_bases = pyairtable.metadata.get_api_bases(api)

    if base_ids is not None:
        base_ids_requested = set(base_ids)
        all_base_ids = {base_record["id"] for base_record in all_bases["bases"]}
        missing_base_ids = base_ids_requested - all_base_ids
        if missing_base_ids:
            msg = f"Base IDs {missing_base_ids} not found in Airtable account."
            raise KeyError(msg)

    for base_record in all_bases["bases"]:
        if (base_record["id"] in base_ids) or (base_ids is None):
            yield BaseRecord(**base_record)


class AirtableBaseToSqlite:
    def __init__(
        self,
        personal_access_token: AirtablePersonalAccessToken,
        db: Database,
        base: BaseRecord,
        prefer_ids: PreferedNamingMethod = PreferedNamingMethod.NAME,
    ):
        self._base = base
        self._db = db
        self._base_api = AirtableBase(personal_access_token, base.id)
        self.prefer_ids = prefer_ids
        self.foreign_keys: ForeignKeySet = set()
        self.table_meta: list[TableSchema] = []
        self.table_id_lookup: dict[str, str] = {}
        self.meta_tables: dict[str, sqlite_utils.db.Table] = {}

    def run(self):
        self.get_schema()
        self.create_metadata_tables()
        self.create_all_table_metadata()
        self.create_foreign_keys()
        self.insert_settings()
        self.insert_all_table_data()

    def get_schema(self):
        logger.info("Fetching schema from Airtable...")
        tables = pyairtable.metadata.get_base_schema(self._base_api)
        for table in tables["tables"]:
            fields = []
            for field in table["fields"]:
                fields.append(FieldSchema(**field))
            views = []
            for view in table["views"]:
                views.append(ViewSchema(**view))
            this_table = TableSchema(
                id=table["id"], name=table["name"], primaryFieldId=table["primaryFieldId"], fields=fields, views=views
            )
            self.table_meta.append(this_table)
            self.table_id_lookup[this_table.id] = this_table.db_name(self.prefer_ids)

    def create_metadata_tables(self):
        for table_name, (columns, options) in META_TABLES.items():
            for foreign_key in options.pop("foreign_keys", []):
                self.foreign_keys.add((table_name, foreign_key))
            db_table = self._db.table(table_name)
            if isinstance(db_table, sqlite_utils.db.Table):
                db_table.create(columns=columns, **options)
                self.meta_tables[table_name] = db_table

    def create_all_table_metadata(self):
        for table in tqdm(self.table_meta):
            self.create_table_metadata(table)

    def get_link_table(self, field: FieldSchema, table: TableSchema) -> Optional[sqlite_utils.db.Table]:
        new_table_name = table.db_name(self.prefer_ids) + "_" + field.id
        link_db_table = self._db.table(new_table_name)
        if isinstance(link_db_table, sqlite_utils.db.Table):
            return link_db_table
        msg = f"Could not find link table {new_table_name}"
        raise ValueError(msg)

    def create_table_metadata(
        self,
        table: TableSchema,
    ):
        table_name = table.db_name(self.prefer_ids)

        self.meta_tables["_meta_table"].insert(
            {
                "id": table.id,
                "name": table.name,
                "primaryFieldId": table.primaryFieldId,
            }
        )
        column_types = {
            "_id": str,
            "_createdTime": datetime,
        }
        fields_to_insert = []
        for field in table.fields:
            field_name = field.db_name(self.prefer_ids)

            choices = field.choices
            if choices is not None:
                self.meta_tables["_meta_field_choice"].insert_all(choices)

            fields_to_insert.append(field.for_insertion(table))

            if (field.type == "multipleRecordLinks") and field.options is not None:
                new_table_name = table_name + "_" + field.id
                other_table = field.options["linkedTableId"]
                other_table_name = self.table_id_lookup.get(other_table, other_table)
                self.foreign_keys.add((new_table_name, ("recordId", table_name, "_id")))
                self.foreign_keys.add((new_table_name, ("otherRecordId", other_table_name, "_id")))
                link_db_table = self._db.table(new_table_name)
                if isinstance(link_db_table, sqlite_utils.db.Table):
                    link_db_table.create(
                        columns={
                            "recordId": str,
                            "otherRecordId": str,
                        },
                    )

            column_type = field.column_type
            if column_type is not None:
                column_types[field_name] = column_type

        self.meta_tables["_meta_field"].insert_all(fields_to_insert)
        db_table = self._db.table(table_name)
        if isinstance(db_table, sqlite_utils.db.Table):
            db_table.create(columns=column_types, pk="_id")

        self.meta_tables["_meta_view"].insert_all(
            {
                "id": view.id,
                "name": view.name,
                "type": view.type,
                "tableId": table.id,
            }
            for view in table.views
        )

    def create_foreign_keys(self):
        logger.info("Adding foreign keys")
        for table_name, foreign_key in self.foreign_keys:
            db_table = self._db[table_name]
            if isinstance(db_table, sqlite_utils.db.Table):
                db_table.add_foreign_key(*foreign_key)

    def insert_settings(self):
        self.meta_tables["_meta_settings"].insert_all(
            [
                {
                    "key": "base_id",
                    "value": self._base.id,
                },
                {
                    "key": "base_name",
                    "value": self._base.name,
                },
                {
                    "key": "permissionLevel",
                    "value": self._base.permissionLevel,
                },
                {
                    "key": "prefer_ids",
                    "value": self.prefer_ids.name,
                },
            ]
        )

    def insert_all_table_data(self):
        logger.info("Fetching table data")
        for table in tqdm(self.table_meta):
            self.insert_table_date(table)

    def insert_table_date(self, table: TableSchema):
        # get table records and insert
        table_data = table.get_table_data(self._base_api)
        table_name = table.db_name(self.prefer_ids)
        db_table = self._db.table(table_name)

        records_to_save = []
        for record in table_data:
            record_to_save = {
                "_id": record["id"],
                "_createdTime": record["createdTime"],
            }
            for field in table.fields:
                if field.type == "multipleRecordLinks":
                    new_table_name = table_name + "_" + field.id
                    link_db_table = self._db.table(new_table_name)
                    if isinstance(link_db_table, sqlite_utils.db.Table):
                        link_db_table.insert_all(
                            {
                                "recordId": record["id"],
                                "otherRecordId": value,
                            }
                            for value in record["fields"].get(field.name, [])
                        )
                else:
                    record_to_save[field.db_name(self.prefer_ids)] = record["fields"].get(field.name)
            records_to_save.append(record_to_save)

        if isinstance(db_table, sqlite_utils.db.Table):
            db_table.insert_all(records_to_save)