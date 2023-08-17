from django.urls import path

from apps.frontend import views

app_name = "frontend"

urlpatterns = [
    path("", views.root, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("note/", views.note_create_or_update_view, name="create"),
    path("note/<int:pk>", views.note_create_or_update_view, name="update"),
]
