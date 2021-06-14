from rest_framework import generics, authentication, permissions, viewsets, mixins
from core.models import User
from .serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# class UserListView(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
class UserListView(generics.RetrieveAPIView):
    # model=User
    serializer_class=UserSerializer
    lookup_field="email"
    queryset = User.objects.all()

    # def get_queryset(self):
    #     print(self.queryset, "somethinghhhhhh")
    #     return User.objects.all()

    def get_object(self):
        return User.objects.first()

    def get_extra_actions(self):
        return None

    def retrieve(self, request, *args, **kwargs):
        print(request, args, kwargs)
        return super().retrieve(request, *args, **kwargs)
