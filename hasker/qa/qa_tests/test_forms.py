from django.test import Client, TestCase
from django.urls import reverse

from hasker.qa.forms import AddQuestionForm
from hasker.qa.models import Question


class AddQuestionFormTest(TestCase):

    def test_empty_form(self):
        form = AddQuestionForm({})
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        data = {'title': 'some title',
                'body': 'some text',
                'form_tags': 't1'}
        form = AddQuestionForm(data)
        self.assertTrue(form.is_valid())

    def test_empty_title(self):
        data = {'title': '',
                'body': 'some text',
                'form_tags': 't1'}
        form = AddQuestionForm(data)
        self.assertFalse(form.is_valid())

    def test_empty_body(self):
        data = {'title': 'some title',
                'body': '',
                'form_tags': 't1'}
        form = AddQuestionForm(data)
        self.assertFalse(form.is_valid())

    def test_empty_tags(self):
        data = {'title': 'some title',
                'body': 'some text',
                'form_tags': ''}
        form = AddQuestionForm(data)
        self.assertFalse(form.is_valid())

    def test_too_many_tags(self):
        data = {'title': 'some title',
                'body': 'some text',
                'form_tags': 't1,'*Question.TAGS_NUM}
        form = AddQuestionForm(data)
        self.assertTrue(form.is_valid())
        data = {'title': 'some title',
                'body': 'some text',
                'form_tags': 't1,'*(Question.TAGS_NUM + 1)}
        form = AddQuestionForm(data)
        self.assertFalse(form.is_valid())

    def test_tags_clean(self):
        data = {'title': 'some title',
                'body': 'some text',
                'form_tags': '  T1  , t2'}
        form = AddQuestionForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['form_tags'], ['t1', 't2'])

    def test_remove_empty_tag(self):
        data = {'title': 'some title',
                'body': 'some text',
                'form_tags': 't1, , ,,,'}
        form = AddQuestionForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['form_tags'], ['t1'])
