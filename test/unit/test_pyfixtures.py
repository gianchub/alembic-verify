from mock import patch, call
import pytest


pytest_plugins = "pytester"


@pytest.fixture
def conftest(testdir):
    testdir.makeconftest(
        """
        import pytest

        @pytest.fixture
        def uri_left():
            return "left"


        @pytest.fixture
        def uri_right():
            return "right"


        @pytest.fixture
        def alembic_root():
            return "root"
        """
    )


@patch('alembicverify.pyfixtures.make_alembic_config')
def test_alembic_config_left(make_config, testdir, conftest):

    testdir.makepyfile(
        """
        def test_config_left(alembic_config_left):
            pass
        """
    )
    result = testdir.runpytest("-s")
    assert result.ret == 0

    assert make_config.call_args_list == [call("left", "root")]


@patch('alembicverify.pyfixtures.make_alembic_config')
def test_alembic_config_right(make_config, testdir, conftest):

    testdir.makepyfile(
        """
        def test_config_right(alembic_config_right):
            pass
        """
    )
    result = testdir.runpytest()
    assert result.ret == 0

    assert make_config.call_args_list == [call("right", "root")]


@patch('alembicverify.pyfixtures.new_db')
@patch('alembicverify.pyfixtures.destroy_database')
def test_new_db_left(
    new_db, destroy_database, conftest, testdir
):
    testdir.makepyfile(
        """
        def test_new_db(new_db_left):
            pass
        """
    )
    result = testdir.runpytest()
    assert result.ret == 0

    assert new_db.call_args_list == [call("left")]
    assert destroy_database.call_args_list == [call("left")]


@patch('alembicverify.pyfixtures.new_db')
@patch('alembicverify.pyfixtures.destroy_database')
def test_new_db_right(
    new_db, destroy_database, conftest, testdir
):
    testdir.makepyfile(
        """
        def test_new_db(new_db_right):
            pass
        """
    )
    result = testdir.runpytest()
    assert result.ret == 0

    assert new_db.call_args_list == [call("right")]
    assert destroy_database.call_args_list == [call("right")]
