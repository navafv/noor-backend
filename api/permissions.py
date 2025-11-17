from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users (Teacher/Staff).
    Uses Django's built-in is_staff flag.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsStudent(permissions.BasePermission):
    """
    Allows access only to registered students.
    Checks if the user has a related 'student' profile.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'student'))


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admins can perform any action.
    Others (Students/Public) can only read (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Similar to IsAdminOrReadOnly, but strictly checks is_staff.
    (This is often synonymous with IsAdmin in this simplified model).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission.
    - Admins can access everything.
    - Students can only access objects that belong to them.
    
    Assumes the model has a 'student' field pointing to the Student model,
    OR a 'user' field pointing to the User model.
    """
    def has_object_permission(self, request, view, obj):
        # Admins are always allowed
        if request.user.is_staff:
            return True

        # Check if object has a 'student' field
        if hasattr(obj, 'student'):
            return obj.student.user == request.user
        
        # Check if object has a 'user' field
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False