# Alembic Verify

Alembic Verify is a library that provides tools to compare database instances
to see if they are in sync.


## Rationale

This library was born to provide a way to make sure that in our production
systems the databases are in sync with the SQLAlchemy models which define
the schemas.
This means that if by applying a migration or manually altering the
database schema we desynchronise the database and the models description,
we now have the means to spot this issue by simply running a test.


## A brief overview on how the library works

This library uses SQLAlchemy inspectors to dig into the schema of a database.
The inspection happens regardless of how the schema was created. This behaviour
is by design, because by detaching the inspection from the way we created
the database we can use the same technique to inspect databases created
with different methods.

We can inspect two databases at a time and create a result object that
holds information about their structure and all the differences they
may exhibit.  In doing so, we can instruct the comparer to ignore some
tables we don't want to be included in the comparison.  This helps
excluding tables that aren't related to the schema or the models we have.

The library at the moment is capable of finding the following differences:

- Differences in tables
- Differences in Primary Keys for a common table
- Differences in Foreign Keys for a common table
- Differences in Indexes for a common table
- Differences in Columns for a common table


## Installation

To install the library... (@Matt: how do we want to distribute this?)


## Compiling the documentation

If you clone the repository, you can access the documentation for the
library.

Create a virtual environment for the project, activate it and install
the dependencies:

    $ pip install -e ".[dev,docs]" --allow-external mysql-connector-python

then change into the ``docs`` folder and run:

    $ make clean html

This command cleans any previous build and creates a fresh one.  Access the
main documentation page at ``docs/build/html/index.html``.


## Testing Examples

There are testing examples to learn how to test your databases using this
library.  There are two modules:

- ``alembicverify.testing.test_example``
- ``alembicverify.testing.test_classic``

The first one shows how to test your databases using pytest, while the
second one shows how to do it with a classical approach based on
``unittest``.

You can run the whole test suite with ``pytest`` by simply running:

    $ py.test

in the root folder of the project.  This will run all tests, including the
classic ones.

Alternatively, you can run only the unittest tests module with this command:

    $ python -m unittest alembicverify/testing/test_classic.py
