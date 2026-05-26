from django.urls import path

from .views import (AssignedTasksView, BoardDetailView, BoardListCreateView,
                    CommentDeleteView, CommentListCreateView, ReviewingTasksView,
                    TaskCreateView, TaskDetailView)

urlpatterns = [
    path('boards/', BoardListCreateView.as_view()),
    path('boards/<int:pk>/', BoardDetailView.as_view()),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view()),
    path('tasks/reviewing/', ReviewingTasksView.as_view()),
    path('tasks/', TaskCreateView.as_view()),
    path('tasks/<int:pk>/', TaskDetailView.as_view()),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view()),
    path('tasks/<int:task_id>/comments/<int:pk>/', CommentDeleteView.as_view()),
]