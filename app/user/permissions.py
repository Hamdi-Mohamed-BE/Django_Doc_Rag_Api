
from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _


class IsOwner(BasePermission):
    message = _("You are not the owner of this object.")

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    

class HasPaidSubscription(BasePermission):
    message = _("You are not a paid user.")

    def has_permission(self, request, view):
        return request.user.has_paid