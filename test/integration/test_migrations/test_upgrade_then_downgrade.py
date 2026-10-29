import pytest
from alembic import command

from alembicverify.util import get_current_revision, prepare_schema_from_migrations
from test.integration.conftest import get_temporary_uri


@pytest.fixture
def alembic_db_uri():
    return get_temporary_uri("postgresql+psycopg2://postgres:postgres@localhost:5433/")


@pytest.mark.parametrize("revision", ["44352f0a4052", "9331f5cd7f8a"])
@pytest.mark.usefixtures("alembic_new_db")
def test_migration_upgrade_and_downgrade(alembic_config, alembic_db_uri, revision):
    engine, script = prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision=f"{revision}@head"
    )

    revisions = []
    while True:
        rev = get_current_revision(alembic_config, engine, script)
        if rev is None:
            break
        command.downgrade(alembic_config, "-1")
        revisions.append(rev)

    assert revisions == [
        revision,
        "591a8001cae9",
        "9182e2f9745a",
        "6c4a48d80d8a",
        "3070a2ba5acc",
    ]

    # engine needs to be disposed manually because we are not using
    # prepare_schema_from_migrations as a context manager
    engine.dispose()


@pytest.mark.parametrize("revision", ["44352f0a4052", "9331f5cd7f8a"])
@pytest.mark.usefixtures("alembic_new_db")
def test_migration_upgrade_and_downgrade_context_manager(alembic_config, alembic_db_uri, revision):
    with prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision=f"{revision}@head"
    ) as (
        engine,
        script,
    ):
        revisions = []
        while True:
            rev = get_current_revision(alembic_config, engine, script)
            if rev is None:
                break
            command.downgrade(alembic_config, "-1")
            revisions.append(rev)

        assert revisions == [
            revision,
            "591a8001cae9",
            "9182e2f9745a",
            "6c4a48d80d8a",
            "3070a2ba5acc",
        ]
