from django.urls import path

from . import views

urlpatterns = [
    path('api/v1/upload/', views.index, name='index'),
    path('api/v1/results/<str:task_id>/', views.results, name='results'),
]
