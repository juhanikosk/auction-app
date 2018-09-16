from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.views.generic.edit import CreateView
from django.shortcuts import render

from auction.models import Item, NewsItem


class IndexView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'items': Item.objects.all(),
            'news': NewsItem.objects.all()
        }

        return render(request, "auction_site/landing_page.html", context)

class CreateAuctionView(CreateView):
    model = Item
    fields = ['name', 'price', 'image']
    template_name = "auction_site/create_auction.html"
