from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import View


from auction.models import AuctionUser


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
        first_name = request.POST.get('first_n')
        last_name = request.POST.get('last_n')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get("password")
        context = {}

        try:
            validate_email(email)
        except ValidationError:
            messages.info(request, 'Enter a valid email address', 'danger')
            return HttpResponseRedirect(reverse('create-user'))

        if len(first_name) < 3 and len(last_name) < 3:
            messages.info(request, "Enter a valid first name and last name.", "danger")
            return HttpResponseRedirect(reverse('create-user'))

        if len(password) < 6:
            messages.info(request, "Password needs to be minimum of 6 characters.", "danger")
            return HttpResponseRedirect(reverse('create-user'))

        try:
            AuctionUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
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
