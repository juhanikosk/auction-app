from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict, Textarea
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import View, DetailView
from django.views.generic.edit import CreateView, UpdateView
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

    def get_form(self):
        form = super(CreateAuctionView, self).get_form()
        form.fields['description'].widget = Textarea(attrs={'class': 'form-control', 'rows': 5})
        return form

    def get_success_url(self):
        messages.success(self.request, "Auction created succesfully.")
        return reverse('auction-confirm', kwargs={'pk': self.object.pk})


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

            if top_bid is None and bid_amount > self.get_object().price or top_bid and bid_amount > top_bid.price:
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
        bid_list = list(auct.bids.order_by('price'))
        price = bid_list[-1].price if bid_list else auct.price
        return {
            'id': auct.id,
            'name': auct.name,
            'current_price': price,
            'description': auct.description,
            'image_url': auct.image.url if auct.image else '/static/img/lataus.png'
        }


class AuctionSearchView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'auction_site/browse_auctions.html')


class AuctionConfirmView(View):
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
