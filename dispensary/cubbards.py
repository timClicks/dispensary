#! /usr/bin/env python
# cubbards

# This file is part of `dispensary`, licenced under the
# GNU General Public License version 3 or later at your
# request.

""" 
Cubbards provide access to

Cubbards attempts to follow the template design pattern.
So, even though each cubbard is specialised to hold its
own contents, such as providing access to an API.

If you wish to make sure that cubbards you 
"""

class Cubbard:
    def get(self, *args, **kwargs):
        raise NotImplementedError

    def put(self, *args, **kwargs):
        raise NotImplementedError

class PlasticCubbard(Cubbard):
    def get(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass

import unittest

class TestCubbard(unittest.TestCase):
    class Broken(Cubbard):
        pass

    def setUp(self):
        self.broken = self.Broken()

    def test_unimplemented_get_causes_problems(self):
        self.assertRaises(NotImplementedError, 
                   self.broken.get, 'anything')

    def test_unimplemented_put_causes_problems(self):
        self.assertRaises(NotImplementedError,
                   self.broken.put, 'anything')

class TestPlasticCubbard(unittest.TestCase):
    class Flexi(PlasticCubbard):
        pass

    def setUp(self):
        self.flexi = self.Flexi()

    def test_unimplemented_get_causes_problems(self):
        self.assertEqual(self.flexi.get(), None)

    def test_unimplemented_put_causes_problems(self):
        self.assertEqual(self.flexi.put(), None)

if __name__ == "__main__":
    unittest.main()
