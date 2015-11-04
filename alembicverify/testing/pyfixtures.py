# -*- coding: utf-8 -*-
import os

import pytest

from .util import (
    get_temporary_uri,
    make_alembic_config,
    new_db,
    safe_destroy_database,
)


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
