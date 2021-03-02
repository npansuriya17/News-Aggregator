from django.urls import path

from . import views

urlpatterns = [
    path("news/<str:category>", views.articles, name="articles"),
    path("feeds/",views.feeds,name="feeds"),
]
