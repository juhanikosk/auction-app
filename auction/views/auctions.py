from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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

    def get_success_url(self):
        messages.success(self.request, "Auction created succesfully.")
        return reverse('auction-details', kwargs={'pk': self.object.pk})


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

            if top_bid is None or bid_amount > top_bid.price and bid_amount > self.get_object().price:
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


class AuctionAPI(View):
    def get(self, request, *args, **kwargs):
        filter_args = {'name__icontains': request.GET.get('title', '')}

        if 'bid' in request.GET:
            try:
                current_bid = int(request.GET.get('bid'))
            except ValueError:
                return HttpResponse('Invalid bid')

            filter_args['bids__price'] = current_bid

        if 'min_bid' in request.GET:
            try:
                current_bid = int(request.GET.get('min_bid'))
            except ValueError:
                return HttpResponse('Invalid bid')

            filter_args['price'] = current_bid

        response = Item.objects.filter(**filter_args)
        return JsonResponse({'auctions': [self.get_auction_dict(auct) for auct in response]})

    def get_auction_dict(self, auct):
        bid_list = list(auct.bids.order_by('price'))
        price = bid_list[-1].price if bid_list else auct.price
        return {
            'id': auct.id,
            'name': auct.name,
            'current_price': price,
            'description': auct.description,
            'image_url': auct.image.url
        }


class AuctionSearchView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'auction_site/browse_auctions.html')
