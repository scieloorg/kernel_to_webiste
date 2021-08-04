from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from .models import Journal
from .forms import CreateUserForm
from .decorators import unauthenticated_user, allowed_users


def home_page(request):
    return render(request, 'home.html', context={})


@login_required(login_url='login')
def user_page(request):
    return render(request, 'user.html', context={})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def journals_page(request):
    num_journals = Journal.objects.all().count()
    context = {'num_journals': num_journals}

    return render(request, 'journals.html', context=context)


@unauthenticated_user
def register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _('User %s was created') % username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context=context)


@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, _('Incorrect username or password'))

    return render(request, 'login.html', context={})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def create_user_page(request):
    return redirect('create_user')


def logout_user(request):
    logout(request)
    return redirect('login')
