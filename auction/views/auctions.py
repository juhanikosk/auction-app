from decimal import Decimal, DecimalException

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict, Textarea
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import View, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render, reverse

from auction.models import Item, NewsItem, Bid


class IndexView(View):
    """
    The main page, which has the most recent auctions listed and also
    news articles, if there are any.
    """
    def get(self, request, *args, **kwargs):
        context = {
            'items': Item.objects.all()[:5],
            'news': NewsItem.objects.all()
        }

        return render(request, "auction_site/landing_page.html", context)


class CreateAuctionView(CreateView):
    """
    A view that is used to create a new auction in the system.
    """
    model = Item
    fields = ['name', 'description', 'price', 'image']
    template_name = "auction_site/create_auction.html"

    def get_form(self):
        form = super(CreateAuctionView, self).get_form()
        form.fields['description'].widget = Textarea(attrs={'class': 'form-control', 'rows': 5})
        return form

    def get_success_url(self):
        messages.success(self.request, "Auction created succesfully.")
        return reverse('auction-confirm', kwargs={'pk': self.object.pk})


class AuctionDetailView(DetailView):
    """
    The view that has information about the auction and the bidding
    details. This is also used to bid on the current auction.
    """
    model = Item
    template_name = "auction_site/auction_details.html"

    def get_context_data(self, **kwargs):
        context = super(AuctionDetailView, self).get_context_data(**kwargs)
        context['top_bid'] = self.get_object().bids.order_by('price').last()
        return context

    def post(self, request, *args, **kwargs):
        threshold = 10000000.00
        bid_amount = request.POST.get('bid-sum')
        if bid_amount:
            top_bid = self.get_object().bids.order_by('price').last()

            try:
                bid_amount = Decimal(bid_amount)
            except DecimalException:
                messages.info(request, 'Invalid value for a bid.', 'danger')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))

            if top_bid is None and bid_amount > self.get_object().price or top_bid and bid_amount > top_bid.price and bid_amount < threshold:
                new_bid = Bid(user=request.user, price=bid_amount, auction=self.get_object(), pending=True)
                new_bid.save()
                messages.success(request, 'Bid placed succesfully.')
                return HttpResponseRedirect(reverse('bid-confirm', kwargs={'pk': new_bid.pk}))
            else:
                messages.info(request, 'Place a higher bid than the current top bid.', 'danger')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))
        else:
            messages.info(request, 'Invalid bid.', 'danger')
            return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))


class AuctionAPI(View):
    """
    An API view that returns information about auctions that fit the
    GET parameters of the request.
    """
    def get(self, request, *args, **kwargs):
        filter_args = {
            'name__icontains': request.GET.get('title', ''),
            'description__icontains': request.GET.get('desc', ''),
        }

        if 'bid' in request.GET:
            try:
                current_bid = int(request.GET.get('bid'))
                filter_args['bids__price'] = current_bid
            except ValueError:
                pass

        response = Item.objects.filter(**filter_args)
        return JsonResponse({'auctions': [self.get_auction_dict(auct) for auct in response]})

    def get_auction_dict(self, auct):
        return {
            'id': auct.id,
            'name': auct.name,
            'current_price': auct.get_top_price,
            'description': auct.description,
            'image_url': auct.image.url if auct.image else '/static/img/lataus.png'
        }


class AuctionSearchView(View):
    """
    A simple view to render the auction browsing view.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'auction_site/browse_auctions.html')


class AuctionConfirmView(View):
    """
    A view that transforms a pending auction into a real auction.
    """
    template_name = 'auction_site/confirm.html'

    def get(self, request, *args, **kwargs):
        object_id = self.kwargs.get('pk')
        try:
            Item.pending_objects.get(pk=object_id)
        except Item.DoesNotExist:
            raise Http404()

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        object_id = self.kwargs.get('pk')
        item = Item.pending_objects.get(pk=object_id)
        item.pending = False
        item.save()
        return HttpResponseRedirect(reverse('auction-details', kwargs=kwargs))


class BidConfirmView(View):
    """
    A view that transforms a pending bid into a real bid.
    """
    template_name = 'auction_site/confirm_bid.html'

    def get(self, request, *args, **kwargs):
        object_id = self.kwargs.get('pk')
        try:
            Bid.pending_objects.get(pk=object_id)
        except Bid.DoesNotExist:
            raise Http404()

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        object_id = self.kwargs.get('pk')
        bid = Bid.pending_objects.get(pk=object_id)
        bid.pending = False
        bid.save()
        return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': bid.auction.id}))
