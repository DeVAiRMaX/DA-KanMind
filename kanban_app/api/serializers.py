from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import Board, Comment, Task


class MemberSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        name = (obj.first_name or '').strip()
        if len(name.split()) < 2:
            name = obj.username
        return name


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def get_author(self, obj):
        return obj.author.first_name


class TaskSerializer(serializers.ModelSerializer):
    assignee = MemberSerializer(read_only=True)
    reviewer = MemberSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'assignee_id', 'reviewer_id',
            'due_date', 'comments_count'
        ]
        extra_kwargs = {'board': {'read_only': True}}

    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

    def get_owner_id(self, obj):
        return obj.owner.id


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_owner_id(self, obj):
        return obj.owner.id

    def get_members(self, obj):
        all_members = list(obj.members.all())
        if obj.owner not in all_members:
            all_members.insert(0, obj.owner)
        return MemberSerializer(all_members, many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    owner_data = MemberSerializer(source='owner', read_only=True)
    members_data = MemberSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members', 'members_data']