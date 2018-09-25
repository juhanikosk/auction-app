"""auction URL Configuration

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.urls import path

from auction.views.login import CreateUserView, LoginView, logout_user
from auction.views.auctions import CreateAuctionView, IndexView, AuctionDetailView, AuctionAPI, AuctionSearchView
from auction.views.user import UserDetailView, UserUpdateView


def login_wrap(view_class, template=None):
    view = view_class.as_view(template) if template else view_class.as_view()
    return login_required(view, login_url='/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', logout_user, name="logout"),
    path('login/create-user/', CreateUserView.as_view(), name="create-user"),
    path('', login_wrap(IndexView), name="main-page"),
    path('create-auction/', login_wrap(CreateAuctionView), name="create-auction"),
    path('auction/<pk>/', login_wrap(AuctionDetailView), name="auction-details"),
    path('user/<pk>/edit', login_wrap(UserUpdateView), name="user-edit-view"),
    path('user/<pk>/', login_wrap(UserDetailView), name="user-detail-view"),
    path('auction/', login_wrap(AuctionAPI), name='auction-api'),
    path('browse/', login_wrap(AuctionSearchView), name='auction-search-view')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
