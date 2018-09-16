from django.contrib import admin
from auction.models import NewsItem

class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

admin.site.register(NewsItem, NewsItemAdmin)
