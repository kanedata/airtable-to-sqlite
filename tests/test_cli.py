import os
import tempfile

from click.testing import CliRunner

import airtable_to_sqlite.__main__ as armain
from airtable_to_sqlite.cli import airtable_to_sqlite

_ = armain


def test_cli(_mock_api, _mock_get_api_bases, _mock_base_schema):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(airtable_to_sqlite, ["--output", os.path.join(tmpdirname, "{}.db"), "app123"])
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(tmpdirname, "Base 123.db"))


def test_cli_error(_mock_api, _mock_get_api_bases, _mock_base_schema):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            airtable_to_sqlite, ["--output", os.path.join(tmpdirname, "blah.db"), "app123", "app124"]
        )
        assert result.exit_code == 2
        assert "Output filename must contain '{}'" in result.output


def test_cli_filename(_mock_api, _mock_get_api_bases, _mock_base_schema):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(airtable_to_sqlite, ["--output", os.path.join(tmpdirname, "blah.db"), "app123"])
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(tmpdirname, "blah.db"))
