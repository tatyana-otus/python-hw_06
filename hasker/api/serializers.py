from rest_framework import serializers

from hasker.qa.models import Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'tags', 'author', 'date',
                  'accepted_answer', 'answers', 'votes']

    def get_votes(self, obj):
        return obj.votes


class AnswerSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Answer
        fields = ['id', 'body', 'author', 'date', 'votes']

    def get_votes(self, obj):
        return obj.votes
