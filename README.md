# Alembic Verify


## Description

Alembic Verify is a library that provides utilities and pytest fixtures to verify that migrations
produce the expected database schema and to prepare the database schema from migrations.


## Table of Contents

- [Alembic Verify](#alembic-verify)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Notable changes in version 1.\*](#notable-changes-in-version-1)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Quick Start](#quick-start)
    - [A quick test example](#a-quick-test-example)
    - [Fixtures Provided](#fixtures-provided)
      - [`alembic_new_db`](#alembic_new_db)
      - [`alembic_config`](#alembic_config)
    - [Utility Functions](#utility-functions)
      - [`prepare_schema_from_migrations(uri, config, revision="head")`](#prepare_schema_from_migrationsuri-config-revisionhead)
      - [`get_current_revision(config, engine, script)`](#get_current_revisionconfig-engine-script)
      - [`get_head_revision(config, engine, script)`](#get_head_revisionconfig-engine-script)
    - [Testing Upgrade/Downgrade Cycles](#testing-upgradedowngrade-cycles)
    - [Branched Migrations](#branched-migrations)
    - [Session for Engine](#session-for-engine)
    - [Deprecated Fixtures](#deprecated-fixtures)
    - [Fixtures that are no longer needed](#fixtures-that-are-no-longer-needed)
    - [Creating custom fixtures](#creating-custom-fixtures)
  - [Development](#development)
    - [Setup](#setup)
    - [Running Tests](#running-tests)
    - [Linting and Formatting](#linting-and-formatting)
    - [Using Tox](#using-tox)
  - [Compatibility](#compatibility)
  - [License](#license)
  - [Contributing](#contributing)


## Notable changes in version 1.*

In this version, the library has been rewritten to be completely untied from the [sqlalchemy-diff](https://github.com/gianchub/sqlalchemy-diff) project.

We have renamed the fixtures to be more consistent and easier to understand. The reason why this work was needed is because the library was born as part of the sqlalchemy-diff project, but then published as a separate project. As a consequence, the naming of the fixtures of the editions prior to 1.* was consistent with the needs of the [sqlalchemy-diff](https://github.com/gianchub/sqlalchemy-diff) project, which is now a totally separate library, to which alembic-verify is no longer related.


## Requirements

- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- SQLAlchemy 1.4.* or 2.0+
- Alembic >= 1.8.0
- pytest >= 7.0.0


## Installation

Install using pip:

```bash
$ pip install alembic-verify
```

Or using uv:

```bash
$ uv pip install alembic-verify
```

## Usage

The library supports any database supported by both [SQLAlchemy](https://www.sqlalchemy.org/) and [sqlalchemy-utils](https://sqlalchemy-utils.readthedocs.io/en/latest/).

### Quick Start

You need to provide two fixtures, which can either live in your test modules, or in the `conftest.py` file of your project, according to your needs.

```python
from uuid import uuid4
import pytest


@pytest.fixture(scope="module")
def alembic_ini_location():
    """Path to your alembic.ini file."""
    return str("path/to/alembic.ini")


@pytest.fixture
def alembic_db_uri():
    """Database URI. Normally in tests you will want a unique temporary database name."""
    base_uri = "postgresql://postgres:postgres@localhost:5432/"
    return f"{base_uri}test_{uuid4().hex}"
```

Once the fixtures are defined, you can proceed to write your migration tests.


### A quick test example

```python
import pytest
from alembicverify.util import prepare_schema_from_migrations


@pytest.mark.usefixtures("alembic_new_db")
def test_migrations(alembic_config, alembic_db_uri):
    with prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision="head"
    ) as (engine, script):
        # All migrations applied successfully
        with engine.connect() as conn:
            # Query your tables, verify schema, etc.
            pass
```

You can also specify a specific revision to apply:

```python
with prepare_schema_from_migrations(
    alembic_db_uri, alembic_config, revision="some_revision"
) as (engine, script):
    # All migrations applied successfully
    pass
```


### Fixtures Provided

The library provides two pytest fixtures:


#### `alembic_new_db`

Creates a temporary database before the test and drops it after. Depends on the `alembic_db_uri` fixture. Use it as a marker:

```python
@pytest.mark.usefixtures("alembic_new_db")
def test_migrations(alembic_config, alembic_db_uri):
    ...
```

This fixture depends on the `alembic_db_uri` fixture.


#### `alembic_config`

Returns a configured `alembic.config.Config` object with:
- Database URL set from your `alembic_db_uri` fixture
- Script location loaded from your `alembic_ini_location` fixture

This fixture depends on both the `alembic_db_uri` and `alembic_ini_location` fixtures.


### Utility Functions


#### `prepare_schema_from_migrations(uri, config, revision="head")`

Applies migrations to the database and returns an engine and script directory.

**Context manager usage** (recommended - automatically disposes the engine):

```python
import pytest
from alembicverify.util import prepare_schema_from_migrations

@pytest.mark.usefixtures("alembic_new_db")
def test_migrations(alembic_config, alembic_db_uri):
    with prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision="head"
    ) as (engine, script):
        # `engine` will be automatically disposed after the context manager exits
        pass
```

**Regular function-style usage** (requires manual disposal of the engine):

```python
import pytest
from alembicverify.util import prepare_schema_from_migrations

@pytest.mark.usefixtures("alembic_new_db")
def test_migration_upgrade_and_downgrade(alembic_config, alembic_db_uri):
    engine, script = prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision="head"
    )
    try:
        # Use engine and script
        pass
    finally:
        engine.dispose()  # Must dispose engine manually
```


#### `get_current_revision(config, engine, script)`

Returns the current applied revision from the database:

```python
import pytest
from alembicverify.util import get_current_revision, prepare_schema_from_migrations

@pytest.mark.usefixtures("alembic_new_db")
def test_migrations(alembic_config, alembic_db_uri):
    with prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision="head"
    ) as (engine, script):
        current = get_current_revision(alembic_config, engine, script)
        assert current == "abc123def456"
```

#### `get_head_revision(config, engine, script)`

Returns the latest (head) revision from the migration chain:

```python
import pytest
from alembicverify.util import get_head_revision, prepare_schema_from_migrations

@pytest.mark.usefixtures("alembic_new_db")
def test_migrations(alembic_config, alembic_db_uri):
    with prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision="head"
    ) as (engine, script):
        head = get_head_revision(alembic_config, engine, script)
        assert head == "abc123def456"
```

### Testing Upgrade/Downgrade Cycles

You can test that migrations can be applied and rolled back:

```python
import pytest
from alembic import command
from alembicverify.util import prepare_schema_from_migrations, get_current_revision


@pytest.mark.usefixtures("alembic_new_db")
def test_migration_upgrade_and_downgrade(alembic_config, alembic_db_uri):
    with prepare_schema_from_migrations(
        alembic_db_uri, alembic_config, revision="head"
    ) as (engine, script):
        # Collect all revisions by downgrading one at a time
        revisions = []
        while True:
            rev = get_current_revision(alembic_config, engine, script)
            if rev is None:
                break
            command.downgrade(alembic_config, "-1")
            revisions.append(rev)

        # Verify the expected revision chain
        assert revisions == [
            "latest_revision",
            "previous_revision",
            "initial_revision",
        ]
```

### Branched Migrations

If your migration history has branches, you can target a specific branch using the `revision@head` syntax:

```python
with prepare_schema_from_migrations(
    alembic_db_uri, alembic_config, revision="branch_revision@head"
) as (engine, script):
    # Migrations applied up to head of the specified branch
    pass
```

### Session for Engine

The library provides a utility function to create a session for an engine. This is useful for testing, for example to verify the application of a migration in detail. You might need to get two different session instances to use before and after the application of a migration.

Here's a full example:

```python
import pytest
from alembic import command
from alembicverify.util import prepare_schema_from_migrations, session_for_engine

down_revision = "44352f0a4052"


@pytest.mark.usefixtures("alembic_new_db")
def test_upgrade(alembic_config, alembic_db_uri):
    with prepare_schema_from_migrations(alembic_db_uri, alembic_config, revision=down_revision) as (
        engine,
        _,
    ):
        with session_for_engine(engine) as session:
            # populate the database, inspect the schema, etc.
            ...

        # then apply the desired migration
        command.upgrade(alembic_config, "+1")

        with session_for_engine(engine) as session:
            # after the migration, verify the schema, its data, etc.
            ...
```

### Deprecated Fixtures

The library provides four deprecated fixtures:

- `new_db_left`: Deprecated in favor of `alembic_new_db`
  - Depends on the `uri_left` fixture
- `new_db_right`: Deprecated in favor of `alembic_new_db`
  - Depends on the `uri_right` fixture
- `alembic_config_left`: Deprecated in favor of `alembic_config`
  - Depends on the `uri_left` fixture and the `alembic_ini_location` fixture
- `alembic_config_right`: Deprecated in favor of `alembic_config`
  - Depends on the `uri_right` fixture and the `alembic_ini_location` fixture

These fixtures are still available for backwards compatibility, but will issue a deprecation warning.

**Note**: The `uri_left` and `uri_right` fixtures are no longer needed when using the library in the new way, they have been replaced by the `alembic_db_uri` fixture.


### Fixtures that are no longer needed

The library no longer uses the `alembic_root` fixture, so you don't need to provide it.


### Creating custom fixtures

In some situations, you may want to spawn more than one random database for your tests.
For example, if you are using `alembic-verify` in combination with `sqlalchemy-diff`, you will
need to spawn two random databases.

You can create custom fixtures by using the factory functions, like in the following example:


```python
from uuid import uuid4
import pytest

from alembicverify import alembic_config_factory, new_db_factory
from alembicverify.util import prepare_schema_from_migrations
from test.integration.conftest import get_temporary_uri


@pytest.fixture
def alembic_db_uri_custom():
    base_uri = "postgresql://postgres:postgres@localhost:5432/"
    return f"{base_uri}test_{uuid4().hex}"


alembic_config_custom = alembic_config_factory(
    alembic_db_uri_fixture_name="alembic_db_uri_custom",
    alembic_ini_location_fixture_name="alembic_ini_location",
    name="alembic_config_custom",
)

alembic_new_db_custom = new_db_factory(
    alembic_db_uri_fixture_name="alembic_db_uri_custom",
    name="alembic_new_db_custom",
)


@pytest.mark.usefixtures("alembic_new_db_custom")
def test_migration_upgrade_and_downgrade_context_manager(
    alembic_config_custom, alembic_db_uri_custom
):
    with prepare_schema_from_migrations(
        alembic_db_uri_custom, alembic_config_custom, revision="head"
    ) as (
        engine,
        script,
    ):
        # use engine and script
```


## Development


### Setup

1. Clone the repository:
   ```bash
   $ git clone https://github.com/gianchub/alembic-verify.git
   $ cd alembic-verify
   ```

2. Install development dependencies:
   ```bash
   $ uv pip install -e .[all]
   ```


### Running Tests

Use the Makefile:

```bash
$ make test
```


### Linting and Formatting

The project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
$ make format
$ make lint
```


### Using Tox

Test across multiple Python and SQLAlchemy versions:

```bash
# Install tox with uv
$ make install-tox-uv

# Run all test environments
$ make tox

# Run specific environment
$ tox -e py314-test-sa14
$ tox -e py314-test-sa20
```


## Compatibility

See the [pyproject.toml](pyproject.toml) file for the requirements.


## License

Apache 2.0. See [LICENSE](LICENSE) for details.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Before submitting a pull request, please ensure that:

- You have added any tests needed to cover the changes you have made
- All tests pass
- The code is formatted correctly
- The documentation (including docstrings and README.md) is up to date
