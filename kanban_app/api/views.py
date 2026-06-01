from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Board, Comment, Task
from .permissions import IsBoardMemberOrOwner, IsCommentAuthor
from .serializers import (BoardDetailSerializer, BoardListSerializer,
                          BoardUpdateSerializer, CommentSerializer,
                          TaskSerializer)


class BoardListCreateView(generics.ListCreateAPIView):
    """Lists all boards the user owns or is a member of; creates a new board."""

    permission_classes = [IsAuthenticated]
    serializer_class = BoardListSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(owner=user) | Board.objects.filter(members=user)

    def perform_create(self, serializer):
        members = self.request.data.get('members', [])
        board = serializer.save(owner=self.request.user)
        board.members.set(members)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves, updates, or deletes a single board."""

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def partial_update(self, request, *args, **kwargs):
        board = self.get_object()
        serializer = BoardUpdateSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            members = request.data.get('members', None)
            board = serializer.save()
            if members is not None:
                board.members.set(members)
            return Response(BoardUpdateSerializer(board).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        board = self.get_object()
        if board.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignedTasksView(generics.ListAPIView):
    """Lists all tasks assigned to the current user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTasksView(generics.ListAPIView):
    """Lists all tasks where the current user is the reviewer."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
    """Creates a new task on a board."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        board_id = self.request.data.get('board')
        board = Board.objects.get(pk=board_id)
        assignee_id = self.request.data.get('assignee_id')
        reviewer_id = self.request.data.get('reviewer_id')
        assignee = User.objects.get(pk=assignee_id) if assignee_id else None
        reviewer = User.objects.get(pk=reviewer_id) if reviewer_id else None
        serializer.save(
            created_by=self.request.user,
            board=board,
            assignee=assignee,
            reviewer=reviewer
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves, updates, or deletes a single task."""

    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def _resolve_user(self, data, key, current):
        if key not in data:
            return current
        return User.objects.get(pk=data[key]) if data[key] else None

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        assignee = self._resolve_user(request.data, 'assignee_id', task.assignee)
        reviewer = self._resolve_user(request.data, 'reviewer_id', task.reviewer)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(assignee=assignee, reviewer=reviewer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if task.created_by != request.user and task.board.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(generics.ListCreateAPIView):
    """Lists all comments for a task; creates a new comment."""

    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_id'])

    def perform_create(self, serializer):
        task = Task.objects.get(pk=self.kwargs['task_id'])
        serializer.save(author=self.request.user, task=task)


class CommentDeleteView(generics.DestroyAPIView):
    """Deletes a comment; only the author is allowed."""

    permission_classes = [IsAuthenticated, IsCommentAuthor]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_id'])

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)