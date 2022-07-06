from django.urls import path

from . import views

urlpatterns = [
    path('api/v1/upload/', views.upload, name='upload'),
    path('api/v1/results/<str:task_id>/', views.results, name='results'),
    path(
        'api/v1/s3-pressigned-url/<str:key>/',
        views.pressigned_url,
        name='pressigned_url',
    ),
    path(
        'api/v1/task-start/<str:key>/<str:filename>/',
        views.task_start,
        name='task_start',
    ),
]
