from decimal import Decimal, DecimalException, InvalidOperation

from django.core import mail
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict, Textarea, HiddenInput
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import View, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render, reverse

from auction.forms.bid import BidForm
from auction.models import AuctionUser, Item, NewsItem, Bid


class IndexView(View):
    """
    The main page, which has the most recent auctions listed and also
    news articles, if there are any.
    """
    def get(self, request, *args, **kwargs):
        context = {
            'items': Item.objects.all().order_by('-created')[:5],
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

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        for key, value in form.fields.items():
            value.widget = HiddenInput()

        if request.FILES:
            imageFile = request.FILES.get('image')
            fs = FileSystemStorage(settings.MEDIA_ROOT)
            filename = fs.save(imageFile.name, imageFile)
            form.fields['image'].widget.attrs['value'] = filename

        data = {
            'form': form,
            'confirm_url': reverse("auction-confirm"),
            'hidden_form': True,
            'confirm_message': 'Are you sure you want to create the auction?'
        }

        return render(request, self.template_name, data)


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
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Access denied")

        bid_amount = request.POST.get('bid-sum')
        if bid_amount:
            top_bid = self.get_object().bids.order_by('price').last()

            try:
                bid_amount = Decimal(bid_amount).quantize(Decimal('0.01'))
            except (DecimalException, InvalidOperation):
                messages.info(request, 'Invalid value for a bid.', 'danger')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))

            threshold = 99999999

            if bid_amount > threshold:
                messages.info(request, 'Bid exceeds the price threshold.', 'danger')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))

            if top_bid is None and bid_amount > self.get_object().price or top_bid and bid_amount > top_bid.price:
                data = {
                    'user': request.user,
                    'price': bid_amount,
                    'auction': self.get_object()
                }

                form = BidForm(data=data)
                for field in form.fields.values():
                    field.widget = HiddenInput()

                return render(request, "auction_site/confirm_bid.html", {'form': form, 'hidden_form': True})
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
        raise Http404()

    def post(self, request, *args, **kwargs):
        item = Item()
        for key, value in request.POST.items():
            setattr(item, key, value)

        item.creator = request.user
        item.save()
        mail.send_mail("Auction has been created.", "A new auction has been succesfully made!", 'juhkoski@abo.fi', [request.user.email])
        messages.success(request, 'Auction created succesfully.')
        return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': item.pk}))


class BidConfirmView(View):
    """
    A view that transforms a pending bid into a real bid.
    """
    template_name = 'auction_site/confirm_bid.html'

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        bid = Bid()
        bid.user = request.user
        bid.auction = Item.objects.get(pk=request.POST.get('auction'))

        price = float(request.POST.get('price'))
        bid.price = Decimal(price).quantize(Decimal('0.01'))

        bid.save()

        messages.success(request, 'Bid placed succesfully.')
        return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': bid.auction.id}))
