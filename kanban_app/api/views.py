from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Board, Comment, Task
from .permissions import (IsBoardMemberOrOwner, IsBoardOwner,
                          IsCommentAuthor, IsTaskCreatorOrBoardOwner)
from .serializers import (BoardDetailSerializer, BoardListSerializer,
                          BoardUpdateSerializer, CommentSerializer,
                          TaskSerializer)


class BoardListCreateView(generics.ListCreateAPIView):
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
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTasksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
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
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        if 'assignee_id' in request.data:
            aid = request.data['assignee_id']
            assignee = User.objects.get(pk=aid) if aid else None
        else:
            assignee = task.assignee
        if 'reviewer_id' in request.data:
            rid = request.data['reviewer_id']
            reviewer = User.objects.get(pk=rid) if rid else None
        else:
            reviewer = task.reviewer
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
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_id'])

    def perform_create(self, serializer):
        task = Task.objects.get(pk=self.kwargs['task_id'])
        serializer.save(author=self.request.user, task=task)


class CommentDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_id'])

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)