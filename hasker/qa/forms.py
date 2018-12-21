from string import Template
from datetime import datetime

from django import forms

from .models import Question, Tag


class QChangeForm(forms.ModelForm):
    header_title = "Ask a question"
    submit_title = "Save"

    form_tags = forms.CharField(required=True)
    class Meta:
        model = Question
        fields = ['title', 'body']

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Title"
        self.fields['body'].label = "Text"
        self.fields['form_tags'].label = "Tags"
        self.user = user
    
    field_order = ['title', 'body', 'form_tags']

    def clean_form_tags(self):
        tags = self.cleaned_data['form_tags'].split(",")
        max_tag_length = Tag._meta.get_field('name').max_length
        if len(tags) > Question.TAGS_NUM:
            raise forms.ValidationError(('Number of tags must be less than: %(len)s'),
                                        code='invalid',
                                        params={'len': Question.TAGS_NUM},
                                        )    
        for t in tags:
            if len(t) > max_tag_length:
                raise forms.ValidationError(("Tag's length must be: %(len)s"),
                                             code='invalid',
                                             params={'len': max_tag_length},
                                            )
        return tags

    def save(self, commit = True): 
        question = super().save(commit = False)
        question.save_new_question(self.user, self.cleaned_data['form_tags'])
