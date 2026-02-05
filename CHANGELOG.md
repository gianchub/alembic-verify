## [1.0.1] - 2026-02-05
  - Pytest as main dependency

## [1.0.0] - 2026-01-28

- Modernized tooling (pyproject.toml, ruff, tox)
- Added support for Python 3.10-3.14
- Added support for SQLAlchemy 1.4 and 2.0
- Removed dependency on sqlalchemy-diff
- Updated test infrastructure
- Added GitHub Actions CI
- Updated the fixtures
- Kept legacy fixtures for backwards compatibility
  - `alembic_root` fixture is no longer needed

## [0.1.4.1] - 2016-11-30

- Release to PyPI

## Version [0.1.3] - 2016-11-29

- Allowed latest SqlAlchemy dependency

## Version [0.1.2] - 2016-10-19

- Relaxed package versions so that they are not pinned down unless it is necessary.
- Makefile added.
- CHANGELOG added.
