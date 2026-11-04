import pytest
from alembic import command
from sqlalchemy import inspect, text

from alembicverify.util import prepare_schema_from_migrations, session_for_engine
from test.integration.conftest import get_temporary_uri


revision = "44352f0a4052"
down_revision = "591a8001cae9"


@pytest.fixture
def alembic_db_uri():
    return get_temporary_uri("postgresql+psycopg2://postgres:postgres@localhost:5433/")


@pytest.mark.usefixtures("alembic_new_db")
def test_upgrade(alembic_config, alembic_db_uri):
    """Demonstrate the technique that can be used to verify the application of a migration
    in detail. It can be applied to any schema or data migration.
    """
    with prepare_schema_from_migrations(alembic_db_uri, alembic_config, revision=down_revision) as (
        engine,
        _,
    ):
        columns = [c["name"] for c in inspect(engine).get_columns("mobile_numbers")]
        assert "is_mobile" not in columns

        # Insert seed data before applying the migration
        with session_for_engine(engine) as session:
            session.execute(text("INSERT INTO companies (id, name) VALUES (1, 'Acme Corp')"))
            session.execute(text("INSERT INTO roles (id, name) VALUES (1, 'Engineer')"))
            session.execute(
                text(
                    "INSERT INTO employees "
                    "(id, name, age, ssn, number_of_pets, company_id, role_id)"
                    " VALUES (1, 'Alice', 30, '123-45-6789', 2, 1, 1)"
                )
            )
            session.execute(
                text(
                    "INSERT INTO mobile_numbers (id, number, owner)"
                    " VALUES (1, '+44-7911-123456', 1)"
                )
            )
            session.commit()

        command.upgrade(alembic_config, revision)

        # Verify the new column exists and existing data is preserved
        with session_for_engine(engine) as session:
            columns = [c["name"] for c in inspect(engine).get_columns("mobile_numbers")]
            assert "is_mobile" in columns

            row = session.execute(
                text("SELECT id, number, owner, is_mobile FROM mobile_numbers WHERE id = 1")
            ).fetchone()
            assert row is not None
            assert row.number == "+44-7911-123456"
            assert row.owner == 1
            assert row.is_mobile is False  # default value from migration


@pytest.mark.usefixtures("alembic_new_db")
def test_downgrade(alembic_config, alembic_db_uri):
    """Demonstrate the technique that can be used to verify the downgrade of a migration
    in detail. It can be applied to any schema or data migration.
    """
    with prepare_schema_from_migrations(alembic_db_uri, alembic_config, revision=revision) as (
        engine,
        _,
    ):
        columns = [c["name"] for c in inspect(engine).get_columns("mobile_numbers")]
        assert "is_mobile" in columns

        # Insert seed data with the is_mobile column populated
        with session_for_engine(engine) as session:
            session.execute(text("INSERT INTO companies (id, name) VALUES (1, 'Acme Corp')"))
            session.execute(text("INSERT INTO roles (id, name) VALUES (1, 'Engineer')"))
            session.execute(
                text(
                    "INSERT INTO employees "
                    "(id, name, age, ssn, number_of_pets, company_id, role_id)"
                    " VALUES (1, 'Alice', 30, '123-45-6789', 2, 1, 1)"
                )
            )
            session.execute(
                text(
                    "INSERT INTO mobile_numbers (id, number, owner, is_mobile)"
                    " VALUES (1, '+44-7911-123456', 1, true)"
                )
            )
            session.commit()

        command.downgrade(alembic_config, down_revision)

        # Verify the is_mobile column is gone but the rest of the data is intact
        with session_for_engine(engine) as session:
            columns = [c["name"] for c in inspect(engine).get_columns("mobile_numbers")]
            assert "is_mobile" not in columns

            row = session.execute(
                text("SELECT id, number, owner FROM mobile_numbers WHERE id = 1")
            ).fetchone()
            assert row is not None
            assert row.number == "+44-7911-123456"
            assert row.owner == 1
