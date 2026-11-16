from django.urls import path
from . import views

app_name = "polls"
urlpatterns = [
    path("", views.home, name="home"),
    path("anket/olustur/", views.create_poll, name="create"),
    path("anketlerim/", views.my_polls, name="my_polls"),
    path("anket/<int:poll_id>/", views.poll_detail, name="detail"),
    path("anket/<int:poll_id>/oyla/", views.cast_vote, name="vote"),
    path("anket/<int:poll_id>/sil/", views.delete_poll, name="delete"),
]
