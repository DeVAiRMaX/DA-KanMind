from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """Grants access only to the board owner or a board member."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()


class IsCommentAuthor(BasePermission):
    """Grants access only to the author of the comment."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user