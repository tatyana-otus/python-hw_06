from django.test import Client, TestCase

from .helper import *


class HelperTest(TestCase):

    def test_parse_search_empty_string(self):
        tag_names, find_value = parse_search_string("")
        self.assertEqual(tag_names, [])
        self.assertEqual(find_value, "")

    def test_parse_search_string(self):
        tag_names, find_value = parse_search_string("tag: tag1_name qwert dfdg")
        self.assertEqual(tag_names, [])
        self.assertEqual(find_value, 'tag: tag1_name qwert dfdg')

    def test_parse_search_string_with_tag(self):
        tag_names, find_value = parse_search_string("tag:tag1_name qwert dfdg")
        self.assertEqual(tag_names, ['tag1_name'])
        self.assertEqual(find_value, 'qwert dfdg')

    def test_parse_search_string_with_tags(self):
        tag_names, find_value = parse_search_string("tag:tag1_name qwert dfdg tag:tag2_name")
        self.assertEqual(tag_names, ['tag1_name', 'tag2_name'])
        self.assertEqual(find_value, 'qwert dfdg')
