from rest_framework import (
    viewsets,
    mixins,
    permissions,
    authentication,
    status,
)
from rest_framework.response import Response

from core.models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.DestroyModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.filter(is_dismissed=False)
    lookup_field = "external_id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_dismissed = True
        notification.save()
        return Response(
            {"data": "dismissed successfully"},
            status=status.HTTP_200_OK,
        )
