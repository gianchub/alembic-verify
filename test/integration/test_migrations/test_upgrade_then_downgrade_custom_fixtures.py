import pytest
from alembic import command

from alembicverify import alembic_config_factory, new_db_factory
from alembicverify.util import get_current_revision, prepare_schema_from_migrations
from test.integration.conftest import get_temporary_uri


@pytest.fixture
def alembic_db_uri_custom():
    return get_temporary_uri("postgresql+psycopg2://postgres:postgres@localhost:5433/")


alembic_config_custom = alembic_config_factory(
    alembic_db_uri_fixture_name="alembic_db_uri_custom",
    alembic_ini_location_fixture_name="alembic_ini_location",
    name="alembic_config_custom",
)

alembic_new_db_custom = new_db_factory(
    alembic_db_uri_fixture_name="alembic_db_uri_custom",
    name="alembic_new_db_custom",
)


@pytest.mark.parametrize("revision", ["44352f0a4052", "9331f5cd7f8a"])
@pytest.mark.usefixtures("alembic_new_db_custom")
def test_migration_upgrade_and_downgrade(alembic_config_custom, alembic_db_uri_custom, revision):
    engine, script = prepare_schema_from_migrations(
        alembic_db_uri_custom, alembic_config_custom, revision=f"{revision}@head"
    )

    revisions = []
    while True:
        rev = get_current_revision(alembic_config_custom, engine, script)
        if rev is None:
            break
        command.downgrade(alembic_config_custom, "-1")
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
@pytest.mark.usefixtures("alembic_new_db_custom")
def test_migration_upgrade_and_downgrade_context_manager(
    alembic_config_custom, alembic_db_uri_custom, revision
):
    with prepare_schema_from_migrations(
        alembic_db_uri_custom, alembic_config_custom, revision=f"{revision}@head"
    ) as (
        engine,
        script,
    ):
        revisions = []
        while True:
            rev = get_current_revision(alembic_config_custom, engine, script)
            if rev is None:
                break
            command.downgrade(alembic_config_custom, "-1")
            revisions.append(rev)

        assert revisions == [
            revision,
            "591a8001cae9",
            "9182e2f9745a",
            "6c4a48d80d8a",
            "3070a2ba5acc",
        ]
