from django.contrib import admin
from auction.models import Bid

class BidsAdmin(admin.ModelAdmin):
    list_display = ('auction', 'price', 'user')

admin.site.register(Bid, BidsAdmin)
