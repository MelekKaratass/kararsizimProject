import re

from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterForm(forms.Form):
    username = forms.CharField(label="Kullanıcı adı", min_length=3, max_length=20)
    email = forms.EmailField(label="E-posta")
    password1 = forms.CharField(label="Parola", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Parolayı tekrar yaz", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not re.fullmatch(r"[a-zA-Z0-9_]{3,20}", username):
            raise ValidationError("3–20 karakter kullan; yalnızca harf, rakam ve alt çizgi yaz.")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Bu kullanıcı adı zaten kullanılıyor.")
        return username.lower()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def clean(self):
        cleaned = super().clean()
        password1, password2 = cleaned.get("password1"), cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Parolalar eşleşmiyor.")
        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as error:
                self.add_error("password1", error)
        return cleaned

    def save(self):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password1"],
        )


class EmailLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="E-posta veya kullanıcı adı",
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )

    def clean(self):
        self.cleaned_data["username"] = self.cleaned_data.get("username", "").strip()
        return super().clean()
