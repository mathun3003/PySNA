# -*- coding: utf-8 -*-
from config import PySNATestCase

from pysna.utils import _string_to_tuple, _tuple_to_string

test_tuple = ("WWU_Muenster", "goetheuni")
test_dict_decoded = {test_tuple: {test_tuple: 0.5, "id": 123}, (123, 456): 0.6}
test_dict_encoded = {"__tuple__['WWU_Muenster', 'goetheuni']": {"id": 123, "__tuple__['WWU_Muenster', 'goetheuni']": 0.5}, "__tuple__[123, 456]": 0.6}


class TestPrivateUtils(PySNATestCase):

    maxDiff = None

    def test_tuples_to_string(self):
        # create results
        dict_results = _tuple_to_string(test_dict_decoded)
        # assert instances
        self.assertIsInstance(dict_results, dict)
        # compare with expected results
        self.assertDictEqual(dict_results, test_dict_encoded)

    def test_string_to_tuple(self):
        # create results
        dict_results = _string_to_tuple(test_dict_encoded)
        # assert instances
        self.assertIsInstance(dict_results, dict)
        # compare with expected results
        self.assertDictEqual(dict_results, test_dict_decoded)
