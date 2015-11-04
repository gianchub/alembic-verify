# -*- coding: utf-8 -*-
import os

import pytest
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


@pytest.fixture(scope="module")
def db_uri():
    return "mysql+mysqlconnector://root:@localhost/alembicverify"


@pytest.fixture(scope="module")
def uri_left(db_uri):
    return get_temporary_uri(db_uri)


@pytest.fixture(scope="module")
def uri_right(db_uri):
    return get_temporary_uri(db_uri)


@pytest.fixture
def alembic_root():
    return os.path.join(os.path.dirname(__file__), 'migrations', 'alembic')


@pytest.fixture
def alembic_config_left(uri_left, alembic_root):
    return make_alembic_config(uri_left, alembic_root)


@pytest.fixture
def alembic_config_right(uri_right, alembic_root):
    return make_alembic_config(uri_right, alembic_root)


@pytest.yield_fixture
def new_db_left(uri_left):
    new_db(uri_left)
    yield
    safe_destroy_database(uri_left)


@pytest.yield_fixture
def new_db_right(uri_right):
    new_db(uri_right)
    yield
    safe_destroy_database(uri_right)


@pytest.mark.usefixtures("new_db_left")
def test_upgrade_and_downgrade(uri_left, alembic_config_left):
    """Test all migrations up and down.

    Tests that we can apply all migrations from a brand new empty
    database, and also that we can remove them all.
    """
    engine, script = prepare_schema_from_migrations(
        uri_left, alembic_config_left)

    head = get_head_revision(alembic_config_left, engine, script)
    current = get_current_revision(alembic_config_left, engine, script)

    assert head == current

    while current is not None:
        command.downgrade(alembic_config_left, '-1')
        current = get_current_revision(alembic_config_left, engine, script)


@pytest.mark.usefixtures("new_db_left")
@pytest.mark.usefixtures("new_db_right")
def test_same_schema_is_the_same(
        uri_left, uri_right, alembic_config_left, alembic_config_right):
    """Compare two databases both from migrations.

    Makes sure the schema comparer validates a database to an exact
    replica of itself.
    """
    prepare_schema_from_migrations(uri_left, alembic_config_left)
    prepare_schema_from_migrations(uri_right, alembic_config_right)

    result = compare(uri_left, uri_right, set(['alembic_version']))

    # uncomment to see the dump of info dict
    # result.dump_info()

    assert True == result.is_match


@pytest.mark.usefixtures("new_db_left")
@pytest.mark.usefixtures("new_db_right")
def test_model_and_migration_schemas_are_not_the_same(
        uri_left, uri_right, alembic_config_left):
    """Compares the database obtained with the first migration against
    the one we get out of the models.  It produces a text file with the
    results to help debug differences.
    """
    prepare_schema_from_migrations(
        uri_left, alembic_config_left, revision="+1")
    prepare_schema_from_models(uri_right)

    result = compare(uri_left, uri_right, set(['alembic_version']))

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
            'left': uri_left,
            'right': uri_right,
        }
    }

    compare_error_dicts(errors, result.errors)


@pytest.mark.usefixtures("new_db_left")
@pytest.mark.usefixtures("new_db_right")
def test_model_and_migration_schemas_are_the_same(
        uri_left, uri_right, alembic_config_left):
    """Compare two databases.

    Compares the database obtained with all migrations against the
    one we get out of the models.  It produces a text file with the
    results to help debug differences.
    """
    prepare_schema_from_migrations(uri_left, alembic_config_left)
    prepare_schema_from_models(uri_right)

    result = compare(uri_left, uri_right, set(['alembic_version']))

    # uncomment to see the dump of errors dict
    # result.dump_errors()

    assert True == result.is_match
