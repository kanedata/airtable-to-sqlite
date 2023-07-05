from enum import Enum
from typing import Dict, NewType, Tuple

OPTION_FIELDS = {
    "linkedTableId": str,
    "isReversed": bool,
    "prefersSingleRecordLink": bool,
    "inverseLinkFieldId": str,
    "isValid": bool,
    "recordLinkFieldId": str,
    "icon": str,
    "color": str,
    "referencedFieldIds": str,
    "result": str,
    "precision": str,
    "symbol": str,
}
NUMBER_FIELD_TYPES = [
    "number",
    "percent",
    "currency",
    "count",
]
META_TABLES: Dict[str, Tuple[Dict, Dict]] = {
    "_meta_table": (
        {
            "id": str,
            "name": str,
            "primaryFieldId": str,
        },
        {"pk": "id", "foreign_keys": [("primaryFieldId", "_meta_field", "id")]},
    ),
    "_meta_field": (
        {
            "id": str,
            "name": str,
            "type": str,
            "tableId": str,
            "options": str,
            **OPTION_FIELDS,
        },
        {
            "pk": ("id", "tableId"),
            "foreign_keys": [
                ("tableId", "_meta_table", "id"),
                ("linkedTableId", "_meta_table", "id"),
                ("inverseLinkFieldId", "_meta_field", "id"),
                ("recordLinkFieldId", "_meta_table", "id"),
            ],
        },
    ),
    "_meta_field_choice": (
        {
            "id": str,
            "name": str,
            "color": str,
            "fieldId": str,
        },
        {"pk": ("id", "fieldId"), "foreign_keys": [("fieldId", "_meta_field", "id")]},
    ),
    "_meta_view": (
        {
            "id": str,
            "name": str,
            "type": str,
            "tableId": str,
        },
        {
            "pk": ("id", "tableId"),
            "foreign_keys": [("tableId", "_meta_table", "id")],
        },
    ),
    "_meta_settings": (
        {
            "key": str,
            "value": str,
        },
        {"pk": "key"},
    ),
}


AirtablePersonalAccessToken = NewType("AirtablePersonalAccessToken", str)

ForeignKeySet = set[Tuple[str, Tuple[str, str, str]]]


class PreferedNamingMethod(Enum):
    NAME = 1
    ID = 2
