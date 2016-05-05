import pytest


@pytest.fixture(scope="module")
def db_uri():
    return "mysql+mysqlconnector://root:password@localhost:3306/alembicverify"
