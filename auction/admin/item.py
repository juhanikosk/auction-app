from django.contrib import admin
from auction.models import Item

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

admin.site.register(Item, ItemAdmin)
