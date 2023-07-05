# Airtable to SQlite

[![PyPI - Version](https://img.shields.io/pypi/v/airtable-to-sqlite.svg)](https://pypi.org/project/airtable-to-sqlite)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airtable-to-sqlite.svg)](https://pypi.org/project/airtable-to-sqlite)

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Database format](#database-format)
- [Alternatives](#alternatives)
- [Future development](#future-development)
- [License](#license)

## Installation

```console
pip install airtable-to-sqlite
```

## Usage

The tool is primarily intended to be used through the command line. Once installed, you can use it like this:

```sh
airtable-to-sqlite app123456789
```

This will fetch the base with the ID `app123456789` and save it to a file called `BaseName.db` in your current directory.

### Authentication

For the tool to work you need to authenticate with Airtable API using a personal access token. To generate a token visit [your Airtable account](https://airtable.com/create/tokens).

There are two ways to use the token. You can set it as an environment variable (called `AIRTABLE_PERSONAL_ACCESS_TOKEN`), and the tool will pick it up:

```sh
export AIRTABLE_PERSONAL_ACCESS_TOKEN=patABCDE123456789
airtable-to-sqlite app123456789
```

Or you can pass it to the tool directly:

```sh
airtable-to-sqlite --personal-access-token patABCDE123456789 app123456789
```

### Download more than one base

You can add more Base IDs to download more than one Base.

```sh
airtable-to-sqlite app123456789 app567891234
```

These will be saved to `Base1Name.db` and `Base2Name.db` respectively.

### Customise the output file

To customise the name of the file where the database will be saved, just pass the `--output` parameter. So for example:

```sh
airtable-to-sqlite --output "output.db" app123456789
```

Will save the file to `output.db`. If you include `{}` in the filename it will be replaced with the name of the base. So for example:

```sh
airtable-to-sqlite --output "db/{}/output.db" app123456789
```

Will result in a file saved to `db/BaseName/output.db`.

The string `{}` must be included if more than one Base is requested, omitting it will produce an error.

### Use IDs instead of names

By default, the tool will use the names of tables, fields and bases. You can use the `--prefer-ids` flag to tell the tool to use the IDs instead. 

If this flag is used it will mean the filenames use the Base ID (eg `app123456789.db` instead of `BaseName.db`), the table names will use IDs instead of names, and columns within the tables will be named using IDs.

This may be helpful if your table or field names contain characters that can't be used in sqlite. You can use the `_meta_table` and `_meta_field` tables (see below) to find the names of the tables and columns

## Database format

Each table within the Airtable Base gets in own table within the database. Each of these tables always contains two default fields, and then the rest of the data from the table. The additional fields are:

- `_id`: The airtable ID for the record. This is set as the primary key
- `_createdTime`: The date and time the record was created.

All fields are stored in the database, with the exception of fields with the type `multipleRecordLinks`, which are instead stored in a linking table.

Where possible, the tool will attempt to assign an appropriate column type to each field. Note that constraints on these fields are not enforced by sqlite by default, so the database may contain invalid data.

### Storage for linked records

Where a field has the type `multipleRecordLinks`, i.e. where it is a record that links to other records in another table, a linking table is created. The name of this table is `{table_name}_{field_id}`, and it always contains two columns, with foreign key constraints to their tables: 

- `recordId`: the record in the original table
- `otherRecordId`: the record in the linked table

Note that these fields contain many-to-many relationships, so values in both fields may appear more than once.

### Meta tables

In addition to the main data tables from the Base, the tool creates tables holding metadata about the original Base and the export process. These tables are:

#### `_meta_table`

A record for each table in the Base. Fields are:

- `id`: (str) Airtable Table ID
- `name`: (str) Table name
- `primaryFieldId`: (str) ID of the primary field

#### `_meta_field`

A record for each field in each table in the Base. Fields are (only the first 4 fields are mandatory):

- `id`: (str) Airtable Field ID
- `name`: (str) Field Name
- `type`: (str) Type of field
- `tableId`: (str) Airtable Table ID
- `options`: (json) Any remaining options not covered by other variables
- `linkedTableId`: (str) For fields of type `multipleRecordLinks`, the other table looked up
- `isReversed`: (bool) 
- `prefersSingleRecordLink`: (bool) 
- `inverseLinkFieldId`: (str) 
- `isValid`: (bool) 
- `recordLinkFieldId`: (str) 
- `icon`: (str) 
- `color`: (str) 
- `referencedFieldIds`: (str) 
- `result`: (str) 
- `precision`: (str) 
- `symbol`: (str) 

#### `_meta_field_choice`

Where a field has choices (e.g. where it is a single or multiple select field), this table contains the options. Fields are:

- `id`: (str) Choice ID
- `name`: (str) Choice Name
- `color`: (str)
- `fieldId`: (str) Airtable Field ID

#### `_meta_view`

A record for each view in the Base. Fields are:

- `id`: (str) Airtable View ID
- `name`: (str) View name
- `tableId`: (str) Airtable Table ID

This table doesn't contain enough information to reconstruct the view.

#### `_meta_settings`

Each record contains a key value pair with a piece of metadata, for example the original Base ID and Base Name. Fields are:

- `key`: (str) 
- `value`: (str) 

## Alternatives

- [`airtable-export` by @simonw](https://github.com/simonw/airtable-export)

## Future development

Potential future developments include:

 - Viewer/editor for exported files
 - Greater coverage of available fields
 - export to Excel (could be a separate tool)

Contributions are very welcome.

## License

`airtable-to-sqlite` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
