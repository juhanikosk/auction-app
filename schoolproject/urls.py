"""schoolproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.urls import path

from schoolproject.views.login import CreateUserView, LoginView
from schoolproject.views.auctions import IndexView


def login_wrap(view_class, template=None):
    view = view_class.as_view(template) if template else view_class.as_view()
    return login_required(view, login_url='/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name="login"),
    path('login/create-user/', CreateUserView.as_view(), name="create-user"),
    path('', login_wrap(IndexView), name="main-page")
]
