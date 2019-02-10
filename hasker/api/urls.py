from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_swagger.views import get_swagger_view

from django.urls import path

from . import views

schema_view = get_swagger_view(title='Hasker API')

app_name = "api"
urlpatterns = [
    path('', schema_view),
    path('questions/', views.IndexQuestionsView.as_view(), name='questions'),
    path('questions/search/', views.IndexQuestionsView.as_view(), name='search'),
    path('questions/<int:pk>', views.QuestionView.as_view(), name='question_detail'),
    path('trending', views.TrendingQuestionsView.as_view(), name='trending'),
    path('questions/<int:pk>/answers', views.AnswersView.as_view(), name='question_answers'),

    path('token/', obtain_jwt_token, name='token_obtain'),
]
