from .permissions import permissions_for_user


def admin_permissions(request):
    return {"admin_permissions": permissions_for_user(request.user)}
