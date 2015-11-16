Alembic Verify
==============

.. pull-quote::

    Verify that your alembic migrations are valid and equivalent to your models.


PyTest Example
--------------


Testing Migrations
^^^^^^^^^^^^^^^^^^

This is how you can verify that your Alembic migrations are valid:

.. literalinclude:: ../testing/test_example.py
    :lines: 6, 10-14, 25-43


Testing Migrations against Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is how you can verify that the databases produced by your migrations
and models are the same.

.. literalinclude:: ../testing/test_example.py
    :lines: 7, 64-79


A full PyTest example
---------------------

Click :ref:`here <full_example>` to see a full PyTest example.


A full Unittest example
-----------------------

If you prefer to use a testing approach based on unittest, you can find
an example on how to do it :ref:`here <full_example_unittest>`.


Features
--------

With this library you will be able to verify the consistency between two
databases, one from Alembic migrations and one from SQLAlchemy models.

The library provides tools for handling migrations and creating all the
required Alembic objects with ease.  Comprehensive examples are included.

The foundation for the comparison is the SQLAlchemy Diff (todo: link)
library.


Installation
------------

.. code-block:: bash

    $ pip install alembic-verify
