# -*- coding: utf-8 -*-
import pytest
from mock import MagicMock, Mock, patch, call

from alembicverify.util import (
    _get_revision,
    get_current_revision,
    get_head_revision,
    make_alembic_config,
    prepare_schema_from_migrations,
)

from test import assert_items_equal


@pytest.yield_fixture
def create_engine_mock():
    with patch('alembicverify.util.create_engine') as m:
        yield m


@pytest.yield_fixture
def Config_mock():
    with patch('alembicverify.util.Config') as m:
        yield m


@pytest.yield_fixture
def ScriptDirectory_mock():
    with patch('alembicverify.util.ScriptDirectory') as m:
        yield m


@pytest.yield_fixture
def command_mock():
    with patch('alembicverify.util.command') as m:
        yield m


@pytest.yield_fixture
def EnvironmentContext_mock():
    with patch('alembicverify.util.EnvironmentContext') as m:
        yield m


@pytest.yield_fixture
def _get_revision_mock():
    with patch('alembicverify.util._get_revision') as m:
        yield m


def test_make_alembic_config(Config_mock):
    config = Config_mock.return_value

    result = make_alembic_config("Config URI", "Config Folder")

    assert config == result
    Config_mock.assert_called_once_with()

    calls_list = [
        call("sqlalchemy.url", "Config URI"),
        call("script_location", "Config Folder")
    ]
    assert_items_equal(calls_list, config.set_main_option.call_args_list)


def test_prepare_schema_for_migrations(
        Config_mock, create_engine_mock, ScriptDirectory_mock, command_mock):
    uri = "Migrations URI"
    config = Config_mock.return_value

    engine, script = prepare_schema_from_migrations(
        uri, config, revision="some revision")

    assert create_engine_mock.return_value == engine
    assert ScriptDirectory_mock.from_config.return_value == script

    create_engine_mock.assert_called_once_with(uri)
    ScriptDirectory_mock.from_config.assert_called_once_with(config)
    command_mock.upgrade.assert_called_once_with(config, "some revision")


def test_prepare_schema_for_migrations_default_revision_value(
        Config_mock, create_engine_mock, ScriptDirectory_mock, command_mock):
    uri = "Migrations URI"
    config = Config_mock.return_value

    engine, script = prepare_schema_from_migrations(uri, config)

    assert create_engine_mock.return_value == engine
    assert ScriptDirectory_mock.from_config.return_value == script

    create_engine_mock.assert_called_once_with(uri)
    ScriptDirectory_mock.from_config.assert_called_once_with(config)
    command_mock.upgrade.assert_called_once_with(config, "head")


def test_get_current_revision(_get_revision_mock):
    config, engine, script = Mock(), Mock(), Mock()

    result = get_current_revision(config, engine, script)

    assert _get_revision_mock.return_value == result
    _get_revision_mock.assert_called_once_with(config, engine, script)


def test_get_head_revision(_get_revision_mock):
    config, engine, script = Mock(), Mock(), Mock()

    result = get_head_revision(config, engine, script)

    assert _get_revision_mock.return_value == result
    _get_revision_mock.assert_called_once_with(
        config, engine, script, revision_type='head')


def test__get_revision_head(EnvironmentContext_mock):
    config, engine, script = Mock(), MagicMock(), Mock()

    revision = _get_revision(config, engine, script, revision_type='head')

    engine.connect.assert_called_once_with()
    EnvironmentContext_mock.assert_called_once_with(config, script)

    env_context = EnvironmentContext_mock().__enter__.return_value
    conn = engine.connect().__enter__.return_value

    env_context.configure.assert_called_once_with(
        conn, version_table='alembic_version')

    env_context.get_head_revision.assert_called_once_with()

    assert env_context.get_head_revision.return_value == revision


def test__get_revision_current(EnvironmentContext_mock):
    config, engine, script = Mock(), MagicMock(), Mock()

    revision = _get_revision(config, engine, script)

    engine.connect.assert_called_once_with()
    EnvironmentContext_mock.assert_called_once_with(config, script)

    env_context = EnvironmentContext_mock().__enter__.return_value
    conn = engine.connect().__enter__.return_value

    env_context.configure.assert_called_once_with(
        conn, version_table='alembic_version')

    env_context.get_context.assert_called_once_with()

    migration_context = env_context.get_context.return_value

    assert migration_context.get_current_revision.return_value == revision
