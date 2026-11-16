from django.urls import path
from .views import EmailLoginView, logout_view, register, registration_success

app_name = "accounts"
urlpatterns = [
    path("kayit/", register, name="register"),
    path("kayit/tamamlandi/", registration_success, name="registration_success"),
    path("giris/", EmailLoginView.as_view(), name="login"),
    path("cikis/", logout_view, name="logout"),
]
