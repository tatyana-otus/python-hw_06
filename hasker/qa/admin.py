from django.contrib import admin

from .models import Question, Answer, Tag


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'body', 'author', 'date',
    	            'show_likes', 'show_dislikes', 'show_tags')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('body', 'author', 'date',
    	            'show_likes', 'show_dislikes')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
