# -*- coding: utf-8 -*-
import os
import unittest

from alembic import command
from sqlalchemydiff import compare
from sqlalchemydiff.util import (
    destroy_database,
    get_temporary_uri,
    new_db,
    prepare_schema_from_models,
)

from alembicverify.util import (
    get_current_revision,
    get_head_revision,
    make_alembic_config,
    prepare_schema_from_migrations,
)
from .models import Base


alembic_root = os.path.join(os.path.dirname(__file__), 'migrations', 'alembic')


class TestExample(unittest.TestCase):

    def setUp(self):
        uri = (
            "mysql+mysqlconnector://root:password@localhost:3306/alembicverify"
        )

        self.uri_left = get_temporary_uri(uri)
        self.uri_right = get_temporary_uri(uri)

        self.alembic_config_left = make_alembic_config(
            self.uri_left, alembic_root)
        self.alembic_config_right = make_alembic_config(
            self.uri_right, alembic_root)

        new_db(self.uri_left)
        new_db(self.uri_right)

    def tearDown(self):
        destroy_database(self.uri_left)
        destroy_database(self.uri_right)

    def test_upgrade_and_downgrade(self):
        """Test all migrations up and down.

        Tests that we can apply all migrations from a brand new empty
        database, and also that we can remove them all.
        """
        engine, script = prepare_schema_from_migrations(
            self.uri_left, self.alembic_config_left)

        head = get_head_revision(self.alembic_config_left, engine, script)
        current = get_current_revision(
            self.alembic_config_left, engine, script)

        assert head == current

        while current is not None:
            command.downgrade(self.alembic_config_left, '-1')
            current = get_current_revision(
                self.alembic_config_left, engine, script)

    def test_model_and_migration_schemas_are_the_same(self):
        """Compare two databases.

        Compares the database obtained with all migrations against the
        one we get out of the models.  It produces a text file with the
        results to help debug differences.
        """
        prepare_schema_from_migrations(self.uri_left, self.alembic_config_left)
        prepare_schema_from_models(self.uri_right, Base)

        result = compare(
            self.uri_left, self.uri_right, set(['alembic_version']))

        assert result.is_match
