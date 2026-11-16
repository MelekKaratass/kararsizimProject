from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = (kwargs.get("email") or username or "").strip()
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username__iexact=identifier)
            except User.DoesNotExist:
                User().set_password(password)
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
