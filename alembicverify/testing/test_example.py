# -*- coding: utf-8 -*-
import os
from uuid import uuid4

from alembic import command
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, drop_database, database_exists
import pytest

from .models import Base
from alembicverify.comparer import compare


db_uri_base = "mysql+mysqlconnector://root:@localhost/alembicverify"
alembic_root_ = os.path.join(
    os.path.dirname(__file__), 'migrations', 'alembic')


@pytest.fixture(scope="module")
def db_uri():
    return db_uri_base


@pytest.fixture(scope="module")
def uri_left(db_uri):
    return _get_temporary_uri(db_uri)


@pytest.fixture(scope="module")
def uri_right(db_uri):
    return _get_temporary_uri(db_uri)


def _get_temporary_uri(db_uri):
    base, _ = db_uri.rsplit('/', maxsplit=1)
    uri = '{}/test_db_{}'.format(base, uuid4().hex)
    return uri


@pytest.fixture
def alembic_root():
    return alembic_root_


@pytest.fixture
def alembic_config_left(uri_left, alembic_root):
    return _make_alembic_config(uri_left, alembic_root)


@pytest.fixture
def alembic_config_right(uri_right, alembic_root):
    return _make_alembic_config(uri_right, alembic_root)


def _make_alembic_config(uri, folder):
    config = Config()
    config.set_main_option("script_location", folder)
    config.set_main_option("sqlalchemy.url", uri)
    return config


@pytest.yield_fixture
def new_db_left(uri_left):
    _new_db(uri_left)
    yield
    _safe_destroy_database(uri_left)


@pytest.yield_fixture
def new_db_right(uri_right):
    _new_db(uri_right)
    yield
    _safe_destroy_database(uri_right)


def _new_db(uri):
    """Drop the database and create a brand new one. """
    _safe_destroy_database(uri)
    create_database(uri)


def _safe_destroy_database(uri):
    if database_exists(uri):
        drop_database(uri)


# # Helpers

def prepare_schema_from_migrations(uri, config):
    engine = create_engine(uri)
    script = ScriptDirectory.from_config(config)
    command.upgrade(config, 'head')
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
    result.dump_info()

    assert True == result.is_match


@pytest.mark.usefixtures("new_db_left")
@pytest.mark.usefixtures("new_db_right")
def test_model_and_migration_schemas_are_the_same(
        uri_left, uri_right, alembic_config_left):
    """Compare two databases.

    Compares the database obtained with the migrations against the one
    we get out of the models.  It produces a text file with the results
    to help debug differences.
    """
    prepare_schema_from_migrations(uri_left, alembic_config_left)
    prepare_schema_from_models(uri_right)

    result = compare(uri_left, uri_right, set(['alembic_version']))

    # uncomment to see the dump of errors dict
    result.dump_errors()

    assert True == result.is_match
