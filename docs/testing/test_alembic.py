# -*- coding: utf-8 -*-
import json
import os

import pytest
from sqlalchemydiff import compare
from sqlalchemydiff.util import prepare_schema_from_models, get_temporary_uri

from alembicverify.util import prepare_schema_from_migrations
from test import assert_items_equal
from .models import Base


@pytest.fixture
def alembic_root():
    return os.path.join(
        os.path.dirname(__file__), 'migrations', 'alembic'
    )


@pytest.fixture(scope="module")
def uri_left(db_uri):
    return get_temporary_uri(db_uri)


@pytest.fixture(scope="module")
def uri_right(db_uri):
    return get_temporary_uri(db_uri)


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

    assert result.is_match


@pytest.mark.usefixtures("new_db_left")
@pytest.mark.usefixtures("new_db_right")
def test_model_and_migration_schemas_are_not_the_same(
        uri_left, uri_right, alembic_config_left):
    """Compares the database obtained with the first migration against
    the one we get out of the models.
    """
    prepare_schema_from_migrations(
        uri_left, alembic_config_left, revision="+1")
    prepare_schema_from_models(uri_right, Base)

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


def compare_error_dicts(err1, err2):
    """Smart comparer of error dicts.

    We cannot directly compare a nested dict structure that has lists
    as values on some level. The order of the same list in the two dicts
    could be different, which would lead to a failure in the comparison,
    but it would be wrong as for us the order doesn't matter and we need
    a comparison that only checks that the same items are in the lists.
    In order to do this, we use the walk_dict function to perform a
    smart comparison only on the lists.

    This function compares the ``tables`` and ``uris`` items, then it does
    an order-insensitive comparison of all lists, and finally it compares
    that the sorted JSON dump of both dicts is the same.
    """
    assert err1['tables'] == err2['tables']
    assert err1['uris'] == err2['uris']

    paths = [
        ['tables_data', 'employees', 'columns', 'left_only'],
        ['tables_data', 'employees', 'columns', 'right_only'],
        ['tables_data', 'employees', 'indexes', 'left_only'],
        ['tables_data', 'employees', 'indexes', 'right_only'],
        ['tables_data', 'employees', 'foreign_keys', 'right_only'],

        ['tables_data', 'phone_numbers', 'columns', 'diff'],
    ]

    for path in paths:
        assert_items_equal(walk_dict(err1, path), walk_dict(err2, path))

    assert sorted(json.dumps(err1)) == sorted(json.dumps(err2))


def walk_dict(d, path):
    """Walks a dict given a path of keys.

    For example, if we have a dict like this::

        d = {
            'a': {
                'B': {
                    1: ['hello', 'world'],
                    2: ['hello', 'again'],
                }
            }
        }

    Then ``walk_dict(d, ['a', 'B', 1])`` would return
    ``['hello', 'world']``.
    """
    if not path:
        return d
    return walk_dict(d[path[0]], path[1:])
