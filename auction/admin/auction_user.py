from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auction.models import AuctionUser

class AuctionUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')

admin.site.register(AuctionUser, AuctionUserAdmin)
