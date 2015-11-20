Alembic Verify
==============

.. pull-quote::

    Verify that your alembic migrations are valid and equivalent to your models.


PyTest Example
--------------


Validating Migrations
^^^^^^^^^^^^^^^^^^^^^

Copy the following test suite into your project to verify that your
migrations are valid. You will have to adapt the ``alembic_root`` and
db related fixture to your structure.  All other fixtures are included
as part of alembic-verify.

.. literalinclude:: ../testing/test_example.py
    :lines: 1-59


Testing Migrations against Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can copy this test in your code to make sure your migrations are
always up to date with your models.  If any change in either of those
would leave them out of sync, this test will fail.

.. literalinclude:: ../testing/test_example.py
    :lines: 62-76


Using unittest
--------------

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
