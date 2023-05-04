from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path("new/", views.NewBookView.as_view(), name="new"),
]