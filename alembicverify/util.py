# -*- coding: utf-8 -*-

from alembic import command
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine


def make_alembic_config(uri, folder):
    """Create a configured :class:`alembic.config.Config` object. """
    config = Config()
    config.set_main_option("script_location", folder)
    config.set_main_option("sqlalchemy.url", uri)
    return config


def prepare_schema_from_migrations(uri, config, revision="head"):
    """Applies migrations to a database.

    :param string uri: The URI for the database.
    :param config: A :class:`alembic.config.Config` instance.
    :param revision: The revision we want to feed to the
        ``command.upgrade`` call. Normally it's either "head" or "+1".
    """
    engine = create_engine(uri)
    script = ScriptDirectory.from_config(config)
    command.upgrade(config, revision)
    return engine, script


def get_current_revision(config, engine, script):
    """Inspection helper. Get the current revision of a set of migrations. """
    return _get_revision(config, engine, script)


def get_head_revision(config, engine, script):
    """Inspection helper. Get the head revision of a set of migrations. """
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
