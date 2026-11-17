import os

from django.contrib.auth import get_user_model
from django.db.models import Q


def axes_username(request, credentials):
    """Treat email and username spellings as one account for login throttling."""
    identifier = credentials.get("username") or credentials.get("email") or ""
    if not isinstance(identifier, str):
        return ""

    identifier = identifier.strip()
    if not identifier:
        return identifier

    user = get_user_model().objects.filter(
        Q(email__iexact=identifier) | Q(username__iexact=identifier)
    ).only("email").first()
    return user.email.casefold() if user else identifier.casefold()


def axes_client_ip(request):
    """Use Vercel's overwritten client-IP header only on Vercel deployments."""
    if os.getenv("VERCEL"):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        client_ip = forwarded_for.split(",", 1)[0].strip()
        if client_ip:
            return client_ip
    return request.META.get("REMOTE_ADDR")
