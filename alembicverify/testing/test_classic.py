# -*- coding: utf-8 -*-

from unittest import TestCase


class ClassicTest(TestCase):

    def test_migrations(self):
        self._test_something(1, 1)

    def _test_something(self, a, b):
        self.assertEqual(a, b)
