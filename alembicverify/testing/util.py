# -*- coding: utf-8 -*-
from uuid import uuid4
import json

from alembic import command
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, drop_database, database_exists

from .models import Base
from test import assert_items_equal


def new_db(uri):
    """Drop the database and create a brand new one. """
    safe_destroy_database(uri)
    create_database(uri)


def safe_destroy_database(uri):
    """Safely destroy a database. """
    if database_exists(uri):
        drop_database(uri)


def get_temporary_uri(uri):
    """From a base URI, create a temporary one. """
    base, _ = uri.rsplit('/', 1)
    uri = '{}/test_db_{}'.format(base, uuid4().hex)
    return uri


def make_alembic_config(uri, folder):
    config = Config()
    config.set_main_option("script_location", folder)
    config.set_main_option("sqlalchemy.url", uri)
    return config


def prepare_schema_from_migrations(uri, config, step="head"):
    engine = create_engine(uri)
    script = ScriptDirectory.from_config(config)
    command.upgrade(config, step)
    return engine, script


def prepare_schema_from_models(uri):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)


def get_current_revision(config, engine, script):
    return _get_revision(config, engine, script)


def get_head_revision(config, engine, script):
    return _get_revision(config, engine, script, revision_type='head')


def _get_revision(config, engine, script, revision_type='current'):
    with engine.connect() as conn:
        with EnvironmentContext(config, script) as env_context:
            env_context.configure(conn, version_table="alembic_version")
            if revision_type == 'head':
                revision = env_context.get_head_revision()
            else:
                migration_context = env_context.get_context()
                revision = migration_context.get_current_revision()
    return revision


def compare_error_dicts(err1, err2):
    """Smart comparison of error dicts.

    We cannot directly compare a nested dict structure that has lists
    as values on some level. The order of the same list in the two dicts
    could be different, which would lead to a failure in the comparison,
    but it would be wrong as for us the order doesn't matter and we need
    a comparison that only checks that the same items are in the lists.
    In order to do this, we use the walk_dict function to perform a
    smart comparison only on the lists.

    This function compares the `tables` and `uris` items, then it does
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

    Then `walk_dict(d, ['a', 'B', 1])` would return ['hello', 'world'].
    """
    if not path:
        return d
    return walk_dict(d[path[0]], path[1:])
