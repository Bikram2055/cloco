from django.urls import path
from . import views


urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("dashboard", views.IndexView.as_view(), name="dashboard"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("logout", views.LogoutView.as_view(), name="logout"),

    path("list-user", views.List_ProductView.as_view(), name="list-product"),
    path("create-user", views.CreateView.as_view(), name="create-product"),
    path(
        "delete-user/<int:pk>",
        views.Delete_ProductView.as_view(),
        name="delete-product",
    ),
    path(
        "update-user/<int:pk>",
        views.Update_ProductView.as_view(),
        name="update-product",
    )
]