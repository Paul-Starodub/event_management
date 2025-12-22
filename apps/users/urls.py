from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from apps.users.views import CreateUserView, ManageUserView, LogoutAPIView

app_name = "users"

urlpatterns = [
    path("", CreateUserView.as_view(), name="create"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
