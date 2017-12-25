from rest_framework.permissions import BasePermission


class IsHaveNotGotTeam(BasePermission):

    def has_permission(self, request, view):
        return not request.user.teams.exists()


class IsHaveGotTeam(BasePermission):

    def has_permission(self, request, view):
        return request.user.teams.exists()


class IsNotAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated()
