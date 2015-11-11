import unittest

from baton.enums import ComparisonOperator
from baton.models import SearchCriteria, SearchCriterion


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
