# SPDX-FileCopyrightText: 2023-present David Kane <david@dkane.net>
#
# SPDX-License-Identifier: MIT

import logging

import click
from sqlite_utils import Database

from airtable_to_sqlite.__about__ import __version__
from airtable_to_sqlite.constants import (
    AirtablePersonalAccessToken,
    PreferedNamingMethod,
)
from airtable_to_sqlite.main import AirtableBaseToSqlite, get_base_records

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="Airtable to SQlite")
@click.option("--personal-access-token", type=AirtablePersonalAccessToken, help="Airtable Personal Access Token")
@click.option("--prefer-ids", is_flag=True, default=False, help="Use Airtable table and field IDs instead of names")
@click.option(
    "--output",
    type=click.Path(exists=False),
    default="{}.db",
    help="Output filename (default: '{}.db'). Use '{}' to insert base name",
)
@click.argument("base-ids", type=str, nargs=-1)
def airtable_to_sqlite(personal_access_token: AirtablePersonalAccessToken, prefer_ids, output, base_ids):
    prefer_ids = PreferedNamingMethod.ID if prefer_ids else PreferedNamingMethod.NAME

    base_records = list(get_base_records(personal_access_token, base_ids))

    if (len(base_ids) > 1) and ("{}" not in output):
        msg = "Output filename must contain '{}' when converting a single base"
        raise click.BadParameter(msg, param_hint="output")

    for base in base_records:
        base_name = base.id if prefer_ids == PreferedNamingMethod.ID else base.name
        database = output.format(base_name)
        db = Database(database, recreate=True)
        AirtableBaseToSqlite(personal_access_token, db, base, prefer_ids).run()
        db.close()
