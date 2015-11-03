# -*- coding: utf-8 -*-
from unittest import TestCase

import six


# Distinction logic in one place
if six.PY2:
    from mock import Mock, patch, call

    class TestCasePatch(TestCase):
        """Provide the assert_items_equal method for testing. """
        def runTest(self, *a, **kwa):  # Hack needed only in Python 2
            pass
    assert_items_equal = TestCasePatch().assertItemsEqual

else:
    from unittest.mock import Mock, patch, call

    assert_items_equal = TestCase().assertCountEqual
