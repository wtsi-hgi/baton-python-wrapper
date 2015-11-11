import unittest
from datetime import date

from baton.enums import ComparisonOperator
from baton.models import SearchCriteria, SearchCriterion, Model


class _StubModel(Model):
    """
    Stub `Model`.
    """
    def __init__(self):
        super(Model, self).__init__()
        self.property_1 = 1
        self.property_2 = "a"
        self.property_3 = []


class TestModel(unittest.TestCase):
    """
    Test cases for `Model`.
    """
    def setUp(self):
        self._model = _StubModel()

    def test_equal_non_nullity(self):
        self.assertNotEqual(self._model, None)

    def test_equal_different_type(self):
        self.assertNotEqual(self._model, date)

    def test_equal_reflexivity(self):
        model = self._model
        self.assertEqual(model, model)

    def test_equal_symmetry(self):
        model1 = self._model
        model2 = self._model
        self.assertEqual(model1, model2)
        self.assertEqual(model2, model1)

    def test_equal_transitivity(self):
        model1 = self._model
        model2 = self._model
        model3 = self._model
        self.assertEqual(model1, model2)
        self.assertEqual(model2, model3)
        self.assertEqual(model1, model3)

    def test_can_get_string_representation(self):
        string_representation = str(self._model)
        self.assertTrue(isinstance(string_representation, str))


class TestSearchCriteria(unittest.TestCase):
    """
    Tests for `SearchCriteria`.
    """
    def setUp(self):
        self._search_criterion1 = SearchCriterion("attribute1", "value1", ComparisonOperator.EQUALS)
        self._search_criterion2 = SearchCriterion("attribute2", "value2", ComparisonOperator.LESS_THAN)

    def test_append_criterion_with_different_attributes(self):
        search_criteria = SearchCriteria()
        search_criteria.append(self._search_criterion1)
        search_criteria.append(self._search_criterion2)
        self.assertCountEqual(search_criteria, [self._search_criterion1, self._search_criterion2])

    def test_append_criterion_with_same_attributes(self):
        search_criteria = SearchCriteria()
        search_criteria.append(self._search_criterion1)
        self.assertRaises(ValueError, search_criteria.append, self._search_criterion1)

    def test_instantiate_with_different_attributes(self):
        search_criteria = SearchCriteria([self._search_criterion1, self._search_criterion2])
        self.assertCountEqual(search_criteria, [self._search_criterion1, self._search_criterion2])

    def test_instantiate_with_same_attributes(self):
        self.assertRaises(ValueError, SearchCriteria, [self._search_criterion1, self._search_criterion1])


if __name__ == '__main__':
    unittest.main()
