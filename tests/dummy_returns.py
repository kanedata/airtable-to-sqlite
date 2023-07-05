BASE_SCHEMA = {
    "tables": [
        {
            "id": "tbl123",
            "name": "My Table",
            "primaryFieldId": "fld123456789A",
            "fields": [
                {"type": "singleLineText", "id": "fld123456789A", "name": "Name"},
                {
                    "type": "singleSelect",
                    "options": {
                        "choices": [
                            {"id": "sel123456789A", "name": "s-1vcpu-3gb", "color": "blueLight2"},
                            {"id": "sel123456789B", "name": "s-1vcpu-2gb", "color": "blueLight2"},
                            {"id": "sel123456789C", "name": "s-6vcpu-16gb", "color": "blueLight2"},
                            {"id": "sel123456789D", "name": "s-8vcpu-16gb", "color": "blueLight2"},
                        ]
                    },
                    "id": "fld123456789B",
                    "name": "Spec",
                },
                {"type": "singleLineText", "id": "fld123456789C", "name": "IP Address"},
                {
                    "type": "multipleRecordLinks",
                    "id": "fld123456789D",
                    "name": "Linked record",
                    "options": {"linkedTableId": "tbl124"},
                },
            ],
            "views": [{"id": "viw123456789", "name": "Grid view", "type": "grid"}],
        },
        {
            "id": "tbl124",
            "name": "My Other Table",
            "primaryFieldId": "fld123456799A",
            "fields": [
                {"type": "singleLineText", "id": "fld123456799A", "name": "Name"},
            ],
            "views": [{"id": "viw123456789A", "name": "Grid view", "type": "grid"}],
        },
    ]
}

DUMMY_RECORDS = [
    [
        {
            "id": "rec123",
            "createdTime": "2021-01-01T00:00:00.000Z",
            "fields": {
                "Name": "Test 3",
                "Number": 123,
                "Checkbox": True,
            },
        },
        {
            "id": "rec124",
            "createdTime": "2021-01-01T00:00:00.000Z",
            "fields": {
                "Name": "Test 4",
                "Number": 124,
                "Checkbox": True,
            },
        },
    ],
    [
        {
            "id": "rec125",
            "createdTime": "2021-01-01T00:00:00.000Z",
            "fields": {
                "Name": "Test 5",
                "Number": 125,
                "Checkbox": True,
            },
        },
        {
            "id": "rec126",
            "createdTime": "2021-01-01T00:00:00.000Z",
            "fields": {
                "Name": "Test 6",
                "Number": 126,
                "Checkbox": False,
            },
        },
    ],
]
GET_API_BASES = {
    "bases": [
        {"id": "app123", "name": "Base 123", "permissionLevel": "create"},
        {"id": "app124", "name": "Base 124", "permissionLevel": "create"},
    ]
}
