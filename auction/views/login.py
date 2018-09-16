from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import View


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login/login.html")

    def post(self, request, *args, **kwargs):
        logout(request)
        username = request.POST.get('username')
        password = request.POST.get("password")
        context = {}

        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                context['message'] = {
                    'text': 'Login success',
                    'type': 'success'
                }

                return HttpResponseRedirect(reverse('main-page'))

        context['message'] = {
            'text': 'Invalid credentials',
            'type': 'danger'
        }

        return render(request, "login/login.html", context)


class CreateUserView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login/create_user.html")

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get("password")
        context = {}

        try:
            User.objects.create_user(
                email=email,
                username=username,
                password=password
            )
        except:
            context['message'] = {
                'type': 'danger',
                'text': "Couldn't create a user"
            }

            return render(request, "login/create_user.html", context)

        messages.success(request, 'User created.')
        return HttpResponseRedirect(reverse('login'))

def logout_user(request, *args, **kwargs):
    logout(request)
    return HttpResponseRedirect(reverse('login'))
