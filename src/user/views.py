from rest_framework.response import Response
from rest_framework import generics, authentication, permissions, views, status
from core.models import User
from .serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


class UserListView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                description="email id of user to search",
                type="str"
            )
        ]
    )
    def get(self, request):
        email = request.query_params.get("email")
        if email:
            user = User.objects.exclude(
                id=self.request.user.id
            ).filter(email=email).first()
            if user:
                return Response(
                    UserSerializer(user).data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "user not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {"error": "missing email"}
        )
