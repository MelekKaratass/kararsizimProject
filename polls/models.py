from django.conf import settings
from django.db import models


class Poll(models.Model):
    CATEGORY_CHOICES = [
        ("gunluk", "Günlük Hayat"),
        ("yemek", "Yemek"),
        ("eglence", "Eğlence"),
        ("alisveris", "Alışveriş"),
        ("egitim_is", "Eğitim / İş"),
        ("seyahat", "Seyahat"),
        ("diger", "Diğer"),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="polls")
    question = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="diger")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=80)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.text


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="votes")
    session_key = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "user"], condition=models.Q(user__isnull=False), name="poll_vote_once_per_user"),
            models.UniqueConstraint(fields=["poll", "session_key"], condition=models.Q(session_key__isnull=False), name="poll_vote_once_per_session"),
        ]

    def __str__(self):
        return f"{self.poll_id}: {self.option}"
