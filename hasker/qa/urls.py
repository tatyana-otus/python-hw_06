from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "qa"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('questions/', views.IndexView.as_view(), name='questions'),
    path('ask/', login_required(views.AddQuestionView.as_view(), 
    	                        login_url='users:login'), name='ask'),
    path('questions/<int:pk>', views.QuestionDetailView.as_view(), name='detail'),
    path('tags/<int:pk>', views.QuestionsByTagView.as_view(), name='tag'),

    path('questions/trending', views.TrendingView.as_view(), name='trending'),
]
