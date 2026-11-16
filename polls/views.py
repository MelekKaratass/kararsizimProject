import json
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PollCreateForm
from .models import Option, Poll, Vote

VOTE_COOKIE = "kararsizim_oy_oturumu"
VOTE_COOKIE_MAX_AGE = 5 * 365 * 24 * 60 * 60


def set_vote_cookie(response, request, browser_id):
    response.set_cookie(
        VOTE_COOKIE,
        browser_id,
        max_age=VOTE_COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
        secure=request.is_secure(),
    )


def home(request):
    polls = Poll.objects.select_related("author").all()
    search_query = request.GET.get("q", "").strip()[:100]
    category_query = request.GET.get("kategori", "").strip()
    category_labels = dict(Poll.CATEGORY_CHOICES)
    if category_query not in category_labels:
        category_query = ""
    if category_query:
        polls = polls.filter(category=category_query)
    if search_query:
        polls = polls.filter(
            Q(question__icontains=search_query)
            | Q(options__text__icontains=search_query)
        ).distinct()
    page = Paginator(polls, 10).get_page(request.GET.get("sayfa"))
    popular_polls = []
    if not search_query:
        popular_polls = (
            polls.select_related("author")
            .annotate(participant_count=Count("votes"))
            .filter(participant_count__gt=0)
            .order_by("-participant_count", "-created_at")[:3]
        )
    return render(request, "polls/home.html", {
        "page": page,
        "popular_polls": popular_polls,
        "search_query": search_query,
        "category_choices": Poll.CATEGORY_CHOICES,
        "selected_category": category_query,
        "selected_category_label": category_labels.get(category_query, ""),
    })


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll.objects.select_related("author").prefetch_related("options"), pk=poll_id)
    browser_id = request.COOKIES.get(VOTE_COOKIE)
    prior_vote = None
    if request.user.is_authenticated:
        prior_vote = Vote.objects.filter(poll=poll, user=request.user).first()
    if prior_vote is None and browser_id:
        prior_vote = Vote.objects.filter(poll=poll, session_key=browser_id).first()
    show_results = request.user == poll.author or prior_vote is not None
    options = poll.options.annotate(vote_count=Count("votes"))
    total_votes = sum(option.vote_count for option in options) if show_results else 0
    option_results = []
    for option in options:
        option_results.append({
            "option": option,
            "votes": option.vote_count,
            "percent": round(option.vote_count * 100 / total_votes) if total_votes else 0,
        })
    response = render(request, "polls/detail.html", {
        "poll": poll, "option_results": option_results, "show_results": show_results,
        "total_votes": total_votes, "prior_vote": prior_vote,
    })
    if browser_id:
        set_vote_cookie(response, request, browser_id)
    return response


@require_POST
def cast_vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    try:
        payload = json.loads(request.body or "{}")
        if not isinstance(payload, dict):
            raise ValueError
        option_id = int(payload.get("option_id", 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "message": "Geçerli bir seçenek seç."}, status=400)
    option = get_object_or_404(Option, pk=option_id, poll=poll)
    browser_id = request.COOKIES.get(VOTE_COOKIE)
    if not browser_id:
        browser_id = uuid.uuid4().hex
    if Vote.objects.filter(poll=poll, session_key=browser_id).exists() or (
        request.user.is_authenticated and Vote.objects.filter(poll=poll, user=request.user).exists()
    ):
        return JsonResponse({"ok": False, "message": "Bu ankette zaten oy kullandın."}, status=409)
    try:
        with transaction.atomic():
            vote = Vote.objects.create(
                poll=poll, option=option,
                user=request.user if request.user.is_authenticated else None,
                session_key=browser_id,
            )
    except IntegrityError:
        return JsonResponse({"ok": False, "message": "Bu ankette zaten oy kullandın."}, status=409)
    response = JsonResponse({"ok": True, "message": "Oyun kaydedildi!", "redirect": f"/anket/{poll.id}/"})
    set_vote_cookie(response, request, browser_id)
    return response


@login_required
def create_poll(request):
    form = PollCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            poll = Poll.objects.create(
                author=request.user,
                question=form.cleaned_data["question"].strip(),
                category=form.cleaned_data["category"],
            )
            Option.objects.bulk_create([
                Option(poll=poll, text=text, position=index)
                for index, text in enumerate(form.cleaned_data["option_values"])
            ])
        messages.success(request, "Anketin yayımlandı!")
        return redirect("polls:detail", poll_id=poll.pk)
    return render(request, "polls/create.html", {"form": form})


@login_required
def my_polls(request):
    polls = Poll.objects.filter(author=request.user).annotate(total_votes=Count("votes"))
    return render(request, "polls/my_polls.html", {"polls": polls})


@login_required
@require_POST
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id, author=request.user)
    poll.delete()
    messages.success(request, "Anketin silindi.")
    return redirect("polls:my_polls")
