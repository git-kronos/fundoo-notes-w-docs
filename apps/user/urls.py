from django.urls import path

from apps.user import views

app_name = "user"
urlpatterns = [
    path("register", views.RegisterAPIView.as_view(), name="register"),
    path("login", views.LoginAPIView.as_view(), name="login"),
    path("profile", views.ProfileAPIView.as_view(), name="profile"),
]
"""
    path("password_reset", views.change_password, name="change_password"),
    path("set_password", views.set_password, name="set_password"),
"""
