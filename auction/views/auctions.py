from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.generic import View, DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import render, reverse

from auction.models import Item, NewsItem, Bid


class IndexView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'items': Item.objects.all(),
            'news': NewsItem.objects.all()
        }

        return render(request, "auction_site/landing_page.html", context)

class CreateAuctionView(CreateView):
    model = Item
    fields = ['name', 'description', 'price', 'image']
    template_name = "auction_site/create_auction.html"


class AuctionDetailView(DetailView):
    model = Item
    template_name = "auction_site/auction_details.html"

    def get_context_data(self, **kwargs):
        context = super(AuctionDetailView, self).get_context_data(**kwargs)
        context['top_bid'] = self.get_object().bids.order_by('price').last()
        return context

    def post(self, request, *args, **kwargs):
        bid_amount = request.POST.get('bid-sum')
        if bid_amount:
            top_bid = self.get_object().bids.order_by('price').last()

            try:
                bid_amount = int(bid_amount)
            except ValueError:
                messages.info(request, 'Invalid value for a bid.', 'danger')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))

            if top_bid is None or bid_amount > top_bid.price:
                new_bid = Bid(user=request.user, price=bid_amount, auction=self.get_object())
                new_bid.save()
                messages.success(request, 'Bid placed succesfully.')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))
            else:
                messages.info(request, 'Place a higher bid than the current top bid.', 'danger')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))
        else:
            messages.info(request, 'Invalid bid.', 'danger')
            return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))
