import logging
from copy import copy
from dataclasses import dataclass
from typing import Any, Optional

from airtable_to_sqlite.constants import (
    NUMBER_FIELD_TYPES,
    OPTION_FIELDS,
    PreferedNamingMethod,
)

logger = logging.getLogger(__name__)


@dataclass
class BaseRecord:
    id: str  # noqa: A003
    name: str
    permissionLevel: str  # noqa: N815


@dataclass
class FieldSchema:
    id: str  # noqa: A003
    name: str
    type: str  # noqa: A003
    options: Optional[dict[str, Any]] = None

    def db_name(self, prefers_ids: PreferedNamingMethod) -> str:
        if prefers_ids == PreferedNamingMethod.ID:
            return self.id
        return self.name

    @property
    def column_type(self) -> Any:
        field_type = self.type
        if field_type == "formula":
            if self.options is not None:
                field_type = self.options.get("result", {}).get("type", field_type)

        if field_type == "multipleRecordLinks":
            return None
        if field_type in NUMBER_FIELD_TYPES:
            return float
        if field_type in ("checkbox"):
            return bool
        return str

    @property
    def choices(self) -> Optional[list[dict[str, Any]]]:
        options = self.options
        if options is None:
            return None

        return [
            {
                "id": choice.get("id"),
                "name": choice.get("name"),
                "color": choice.get("color"),
                "fieldId": self.id,
            }
            for choice in options.get("choices", [])
        ]

    def for_insertion(self, table: "TableSchema"):
        options = copy(self.options)
        field_to_insert: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "tableId": table.id,
        }
        if options is None:
            for option_field in OPTION_FIELDS.keys():
                field_to_insert[option_field] = None
        else:
            for option_field in OPTION_FIELDS.keys():
                field_to_insert[option_field] = options.pop(option_field, None)
        field_to_insert["options"] = options
        return field_to_insert


@dataclass
class ViewSchema:
    id: str  # noqa: A003
    name: str
    type: str  # noqa: A003

    def db_name(self, prefers_ids: PreferedNamingMethod) -> str:
        if prefers_ids == PreferedNamingMethod.ID:
            return self.id
        return self.name


@dataclass
class TableSchema:
    id: str  # noqa: A003
    name: str
    primaryFieldId: str  # noqa: N815
    fields: list[FieldSchema]
    views: list[ViewSchema]

    def db_name(self, prefers_ids: PreferedNamingMethod) -> str:
        if prefers_ids == PreferedNamingMethod.ID:
            return self.id
        return self.name

    def get_table_data(self, api):
        logger.info(f"Fetching table data for {self.name} from Airtable...")
        return api.all(self.name)
