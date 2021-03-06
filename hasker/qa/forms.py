from string import Template
from datetime import datetime

from django import forms

from .models import Question, Tag, Answer


class AddQuestionForm(forms.ModelForm):
    header_title = "Ask a question"
    submit_title = "Save"
    field_order = ['title', 'body', 'form_tags']
    form_tags = forms.CharField(required=True, label='Tags')

    class Meta:
        model = Question
        fields = ['title', 'body']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_form_tags(self):
        tags = self.cleaned_data['form_tags'].lower()
        tags = [t.strip() for t in tags.split(",") if t.strip()]
        max_tag_length = Tag._meta.get_field('name').max_length
        if len(tags) > Question.TAGS_NUM:
            raise forms.ValidationError('Number of tags must be less than: %(len)s',
                                        code='invalid',
                                        params={'len': Question.TAGS_NUM},
                                        )
        for t in tags:
            if len(t) > max_tag_length:
                raise forms.ValidationError("Tag's length must be: %(len)s",
                                            code='invalid',
                                            params={'len': max_tag_length},
                                            )
        return tags

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.save_new_question(author, self.cleaned_data['form_tags'])


class AddAnswerForm(forms.ModelForm):
    header_title = "Your answer"
    submit_title = "Submit"

    class Meta:
        model = Answer
        fields = ['body']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].label = ""

    def save(self, author, question_pk, commit=True):
        answer = super().save(commit=False)
        answer.save_new_answer(author, question_pk, self.cleaned_data['body'])
