from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "qa"
urlpatterns = [
    path('', views.IndexView.as_view(), name='questions'),
    path('ask/', login_required(views.AddQuestionView.as_view(),
                                login_url='users:login'), name='ask'),
    path('update', login_required(views.update_votes,
                                 login_url='users:login'), name='update'),
    path('<int:pk>/', views.QA_DetailView.as_view(), name='detail'),
    path('tags/<int:pk>/', views.QuestionsByTagView.as_view(), name='tag'),
    path('trending', views.TrendingView.as_view(), name='trending'),
]
