from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "qa"
urlpatterns = [
    path('ask/', login_required(views.AddQuestionView.as_view(),
                                login_url='users:login'), name='ask'),

    path('<int:pk>/answers/', views.AnswerView.as_view(), name='answers'),
    path('<int:pk>', views.QuestionDetailView.as_view(), name='detail'),
    path('tags/<int:pk>', views.QuestionsByTagView.as_view(), name='tag'),

    path('trending', views.TrendingView.as_view(), name='trending'),
    path('', views.IndexView.as_view(), name='questions'),

    path('update', login_required(views.update_votes,
                                 login_url='users:login'), name='update'),
]
