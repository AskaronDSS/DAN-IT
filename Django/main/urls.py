from django.urls import path
from . import views

urlpatterns = [
    path('history/clear/', views.clear_history, name='clear_history'),
    path('home/', views.home, name='home'),
    path('login/', views.my_login, name='login'),
    path('forecast/', views.predict_view, name='forecast'),
    path('history/', views.history, name='history'),
    path('analise/', views.statistics, name='analise'),
    path('', views.register, name='register'),
]