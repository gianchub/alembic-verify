Alembic Verify
==============

.. pull-quote::

    A library that allows developer to quickly check if two database schemas
    are in sync.

A quick example
---------------

Here's how you could write a test that compares two schemas, using ``pytest``:

.. code-block:: Python

    @pytest.mark.usefixtures("new_db_left")
    @pytest.mark.usefixtures("new_db_right")
    def test_model_and_migration_schemas_are_the_same(
            uri_left, uri_right, alembic_config_left):

        # uri_left DB created from migrations
        prepare_schema_from_migrations(uri_left, alembic_config_left)

        # uri_right DB created from SQLAlchemy models
        prepare_schema_from_models(uri_right)

        result = compare(uri_left, uri_right, set(['alembic_version']))

        assert True == result.is_match


If the schemas are different the test will fail, and you will be able to
dump the differences by just adding one simple line of code:

.. code-block:: Python

    result.dump_errors()


This will dump to a file a JSON dictionary that looks like this:


.. code-block::

    {
        'tables': {
            'left_only': ['addresses'],
            'right_only': ['roles']
        },
        'tables_data': {
            'employees': {
                'columns': {
                    'left_only': [
                        {
                            'default': None,
                            'name': 'favourite_meal',
                            'nullable': False,
                            'type': "ENUM('meat','vegan','vegetarian')"
                        }
                    ],
                    'right_only': [
                        {
                            'autoincrement': False,
                            'default': None,
                            'name': 'role_id',
                            'nullable': False,
                            'type': 'INTEGER(11)'
                        },
                        {
                            'autoincrement': False,
                            'default': None,
                            'name': 'number_of_pets',
                            'nullable': False,
                            'type': 'INTEGER(11)'
                        },
                    ]
                },
                'foreign_keys': { ... },
                'primary_keys': { ... },
                'indexes': { .. }
            },
            'phone_numbers': { ... }
        },
        'uris': {
            'left': "your left URI",
            'right': "your right URI",
        }
    }


If you prefer a more classical testing approach using ``unittest``, this
is how you could go about it:

.. code-block:: Python

     class TestCompare(TestCase):

        def setUp(self):
            uri = "mysql+mysqlconnector://root:@localhost/alembicverify"
            alembic_root = os.path.join(
                os.path.dirname(__file__), 'migrations', 'alembic')

            self.uri_left = get_temporary_uri(uri)
            self.uri_right = get_temporary_uri(uri)

            self.alembic_config_left = make_alembic_config(
                self.uri_left, alembic_root)
            self.alembic_config_right = make_alembic_config(
                self.uri_right, alembic_root)

            new_db(self.uri_left)
            new_db(self.uri_right)

        def tearDown(self):
            destroy_database(self.uri_left)
            destroy_database(self.uri_right)

        def test_model_and_migration_schemas_are_the_same(self):
            prepare_schema_from_migrations(self.uri_left, self.alembic_config_left)
            prepare_schema_from_models(self.uri_right)

            result = compare(
                self.uri_left, self.uri_right, set(['alembic_version']))

            self.assertTrue(result.is_match)


Features
--------

Currently the library can detect the following differences:

- Differences in **Tables**
- Differences in **Primary Keys** for a common table
- Differences in **Foreign Keys** for a common table
- Differences in **Indexes** for a common table
- Differences in **Columns** for a common table


Installation
------------

.. code-block::

    $ pip install alembic-verify


Usage
-----

- Compare databases with ``compare``
- Utilities
    - Test examples (``pytest``)
    - Test examples (``unittest``)
