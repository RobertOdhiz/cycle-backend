from rest_framework import permissions

class IsRenterOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role == 'RENTER' or request.user.role == 'ADMIN':
                return True
            return False
        return view.action in ['list', 'retrieve']