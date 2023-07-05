# SPDX-FileCopyrightText: 2023-present David Kane <david@dkane.net>
#
# SPDX-License-Identifier: MIT
import sys

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    from airtable_to_sqlite.cli import airtable_to_sqlite

    sys.exit(airtable_to_sqlite(auto_envvar_prefix="AIRTABLE"))
