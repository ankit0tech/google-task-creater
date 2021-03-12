from django.urls import path, include
from task import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('task', views.TaskViewSet, basename='task')

app_name = 'tasks'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/<int:pk>/', include(router.urls)),
    path('create_task/', views.create_task, name='create_task'),
    path('update_task/<int:pk>/', views.update_task, name='update_task'),
    path('delete_task/<int:pk>/', views.delete_task, name='delete_task'),
    path('tasks_list/', views.tasks_list, name='tasks_list'),
]