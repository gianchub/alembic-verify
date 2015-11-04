# -*- coding: utf-8 -*-

"""
This test suite is just to demonstrate how one could test their models
and migrations using this library and a classical approach based on
unittest.
"""

import os
from unittest import TestCase

from alembic import command

from .util import (
    get_current_revision,
    get_head_revision,
    get_temporary_uri,
    make_alembic_config,
    new_db,
    prepare_schema_from_migrations,
    prepare_schema_from_models,
    safe_destroy_database,
    compare_error_dicts,
)
from alembicverify.comparer import compare


class TestCompare(TestCase):

    def setUp(self):
        uri = "mysql+mysqlconnector://root:@localhost/alembicverify"
        alembic_root = os.path.join(
            os.path.dirname(__file__), 'migrations', 'alembic')

        self.uri_left = get_temporary_uri(uri)
        self.uri_right = get_temporary_uri(uri)

        self.alembic_config_left = make_alembic_config(
            self.uri_left, alembic_root)
        self.alembic_config_right = make_alembic_config(
            self.uri_right, alembic_root)

        new_db(self.uri_left)
        new_db(self.uri_right)

    def tearDown(self):
        safe_destroy_database(self.uri_left)
        safe_destroy_database(self.uri_right)

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

        self.assertEqual(head, current)

        while current is not None:
            command.downgrade(self.alembic_config_left, '-1')
            current = get_current_revision(
                self.alembic_config_left, engine, script)

    def test_same_schema_is_the_same(self):
        """Compare two databases both from migrations.

        Makes sure the schema comparer validates a database to an exact
        replica of itself.
        """
        prepare_schema_from_migrations(
            self.uri_left, self.alembic_config_left)
        prepare_schema_from_migrations(
            self.uri_right, self.alembic_config_right)

        result = compare(
            self.uri_left, self.uri_right, set(['alembic_version']))

        # uncomment to see the dump of info dict
        # result.dump_info()

        self.assertTrue(result.is_match)

    def test_model_and_migration_schemas_are_not_the_same(self):
        """Compares the database obtained with the first migration against
        the one we get out of the models.  It produces a text file with the
        results to help debug differences.
        """
        prepare_schema_from_migrations(
            self.uri_left, self.alembic_config_left, revision="+1")
        prepare_schema_from_models(self.uri_right)

        result = compare(
            self.uri_left, self.uri_right, set(['alembic_version']))

        # uncomment to see the dump of errors dict
        # result.dump_errors()

        errors = {
            'tables': {
                'left_only': ['addresses'],
                'right_only': ['roles']
            },
            'tables_data': {
                'employees': {
                    'columns': {
                        'left_only': [
                            {
                                'default': None,
                                'name': 'favourite_meal',
                                'nullable': False,
                                'type': "ENUM('meat','vegan','vegetarian')"
                            }
                        ],
                        'right_only': [
                            {
                                'autoincrement': False,
                                'default': None,
                                'name': 'role_id',
                                'nullable': False,
                                'type': 'INTEGER(11)'
                            },
                            {
                                'autoincrement': False,
                                'default': None,
                                'name': 'number_of_pets',
                                'nullable': False,
                                'type': 'INTEGER(11)'
                            },
                        ]
                    },
                    'foreign_keys': {
                        'right_only': [
                            {
                                'constrained_columns': ['role_id'],
                                'name': 'fk_employees_roles',
                                'options': {},
                                'referred_columns': ['id'],
                                'referred_schema': None,
                                'referred_table': 'roles'
                            }
                        ]
                    },
                    'indexes': {
                        'left_only': [
                            {
                                'column_names': ['name'],
                                'name': 'name',
                                'type': 'UNIQUE',
                                'unique': True
                            }
                        ],
                        'right_only': [
                            {
                                'column_names': ['role_id'],
                                'name': 'fk_employees_roles',
                                'unique': False
                            },
                            {
                                'column_names': ['name'],
                                'name': 'ix_employees_name',
                                'type': 'UNIQUE',
                                'unique': True
                            }
                        ]
                    }
                },
                'phone_numbers': {
                    'columns': {
                        'diff': [
                            {
                                'key': 'number',
                                'left': {
                                    'default': None,
                                    'name': 'number',
                                    'nullable': True,
                                    'type': 'VARCHAR(40)'
                                },
                                'right': {
                                    'default': None,
                                    'name': 'number',
                                    'nullable': False,
                                    'type': 'VARCHAR(40)'
                                }
                            }
                        ]
                    }
                }
            },
            'uris': {
                'left': self.uri_left,
                'right': self.uri_right,
            }
        }

        compare_error_dicts(errors, result.errors)

    def test_model_and_migration_schemas_are_the_same(self):
        """Compare two databases.

        Compares the database obtained with all migrations against the
        one we get out of the models.  It produces a text file with the
        results to help debug differences.
        """
        prepare_schema_from_migrations(self.uri_left, self.alembic_config_left)
        prepare_schema_from_models(self.uri_right)

        result = compare(
            self.uri_left, self.uri_right, set(['alembic_version']))

        # uncomment to see the dump of errors dict
        # result.dump_errors()

        self.assertTrue(result.is_match)
