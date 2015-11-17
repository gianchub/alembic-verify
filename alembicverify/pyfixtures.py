# -*- coding: utf-8 -*-
import pytest

from sqlalchemydiff.util import destroy_database, new_db

from alembicverify.util import make_alembic_config


@pytest.fixture
def alembic_config_left(uri_left, alembic_root):
    """Requires alembic_root fixture to be defined. """
    return make_alembic_config(uri_left, alembic_root)


@pytest.fixture
def alembic_config_right(uri_right, alembic_root):
    """Requires alembic_root fixture to be defined. """
    return make_alembic_config(uri_right, alembic_root)


@pytest.yield_fixture
def new_db_left(uri_left):
    new_db(uri_left)
    yield
    destroy_database(uri_left)


@pytest.yield_fixture
def new_db_right(uri_right):
    new_db(uri_right)
    yield
    destroy_database(uri_right)
