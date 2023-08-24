from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.frontend.forms import NoteForm, RegistrationForm
from apps.note.models import Note
from apps.utils.paginator import paginate_obj


# Create your views here.
@login_required
def root(request: HttpRequest) -> HttpResponse:
    notes = Note.objects.owner_notes(owner=request.user)
    page_obj = paginate_obj(notes, request)
    return render(request, "index.html", {"po": page_obj})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")
    else:
        form = AuthenticationForm(request)
    return render(request, "auth.html", {"form": form, "title": "Login Form"})


def register_view(request: HttpRequest) -> HttpResponse:
    form = RegistrationForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.set_password(form.cleaned_data["password"])
            obj.save()
            return redirect("frontend:login")
    return render(request, "auth.html", {"form": form, "page": "Register Form"})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("/")


@login_required
def note_create_or_update_view(request: HttpRequest, pk=None) -> HttpResponse:
    form_args = {
        "user": request.user,
        "auto_id": "%s",
        "data": request.POST or None,
        "initial": {"title": "Initial title", "body": "Initial body"},
        "instance": None,
    }
    page = "Create Note"
    if pk:
        form_args.update(initial=None, instance=Note.objects.owner_notes(owner=request.user).get(pk=pk))
        page = "Update Note"

    form = NoteForm(**form_args)

    if form.is_valid():
        form.save()
        return redirect("/")
    else:
        print(form.errors)

    return render(request, "note_form.html", {"form": form, "page": page})
