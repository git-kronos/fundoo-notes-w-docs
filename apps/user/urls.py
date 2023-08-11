from django.urls import path

from apps.user import views

app_name = "user"
urlpatterns = [
    path("register", views.user_register, name="register"),
    path("login", views.user_login, name="login"),
    path("profile", views.user_profile, name="profile"),
]
"""
    path("password_reset", views.change_password, name="change_password"),
    path("set_password", views.set_password, name="set_password"),
"""
