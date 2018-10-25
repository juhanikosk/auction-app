from datetime import timedelta
from decimal import Decimal, DecimalException, InvalidOperation

from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict, Textarea, HiddenInput, IntegerField
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render, reverse
from django.utils.timezone import now

from auction.forms.bid import BidForm
from auction.models import AuctionUser, Item, NewsItem, Bid


class IndexView(View):
    """
    The main page, which has the most recent auctions listed and also
    news articles, if there are any.
    """
    def get(self, request, *args, **kwargs):
        context = {
            'items': Item.objects.filter(status='AC').order_by('-created')[:5],
            'news': NewsItem.objects.all()
        }

        return render(request, "auction_site/landing_page.html", context)


class CreateAuctionView(CreateView):
    """
    A view that is used to create a new auction in the system.
    """
    model = Item
    fields = ['name', 'description', 'price', 'deadline', 'image']
    template_name = "auction_site/create_auction.html"

    def get_form(self):
        form = super(CreateAuctionView, self).get_form()
        form.fields['description'].widget = Textarea(attrs={'class': 'form-control', 'rows': 5})
        form.fields['deadline'] = IntegerField(max_value=336, min_value=72)
        form.fields['deadline'].help_text = "Deadline in hours from now. Needs to be a number between 72 and 336."
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        for key, value in form.fields.items():
            value.widget = HiddenInput()

        if request.FILES:
            imageFile = request.FILES.get('image')
            fs = FileSystemStorage()
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

        bid_amount = float(request.POST.get('bid-sum'))
        if bid_amount:
            top_bid = self.get_object().bids.order_by('price').last()

            if not top_bid and bid_amount < self.get_object().price or top_bid and bid_amount < top_bid.price:
                messages.info(request, 'Place a higher bid than the current top bid.', 'danger')
                return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': self.get_object().pk}))

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
                current_bid = float(request.GET.get('bid'))
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
            'image_url': auct.image.url if auct.image else '/static/img/lataus.png',
            'status': auct.status
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
            if key == 'deadline':
                try:
                    hours = int(value)
                except ValueError:
                    messages.info(request, 'Invalid deadline.', 'danger')
                    return HttpResponseRedirect(reverse('create-auction'))

                if (hours < 72 or hours > 336):
                    messages.info(request, 'Invalid deadline.', 'danger')
                    return HttpResponseRedirect(reverse('create-auction'))

                item.deadline = now() + timedelta(hours=hours)
            else:
                setattr(item, key, value)

        item.creator = request.user
        item.save()
        mail.send_mail("Auction has been created.", "A new auction has been succesfully made!", 'juhkoski@abo.fi', [request.user.email])
        messages.success(request, 'Auction created succesfully.')
        return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': item.pk}))


class BidConfirmView(View):
    """
    A view that is used to confirm a bid.
    """
    template_name = 'auction_site/confirm_bid.html'

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        auction = Item.objects.get(pk=request.POST.get('auction'))
        if auction.status != 'AC':
            messages.info(request, "The auction is not active.", 'danger')
            return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': auction.pk})) 

        if request.user == auction.creator:
            messages.info(request, "Sellers can't bid their own auctions.", 'danger')
            return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': auction.pk})) 

        bid = Bid()
        bid.user = request.user
        bid.auction = auction
        bid_amount = float(request.POST.get('price'))

        try:
            bid_amount = Decimal(bid_amount).quantize(Decimal('0.01'))
        except (DecimalException, InvalidOperation):
            messages.info(request, 'Invalid value for a bid.', 'danger')
            return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': auction.pk}))

        top_bid = auction.bids.order_by('price').last()

        if top_bid is None and bid_amount > auction.price or top_bid and bid_amount > top_bid.price:
            bid.price = bid_amount
        else:
            messages.info(request, 'Place a higher bid than the current top bid.', 'danger')
            return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': auction.pk}))

        bid.save()

        mail.send_mail("A new bid has been placed.", "A new greater bid has been succesfully placed!", 'juhkoski@abo.fi', [auction.creator])
        mail.send_mail("A new bid has been placed.", "A new greater bid has been succesfully placed!", 'juhkoski@abo.fi', [auction.creator])
        messages.success(request, 'Bid placed succesfully.')
        return HttpResponseRedirect(reverse('auction-details', kwargs={'pk': bid.auction.id}))


class AuctionUpdateView(UpdateView):
    model=Item
    fields=["description"]
    template_name="auction_site/standard_form.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(creator=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(AuctionUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = "Update description"
        return context

    def get_form(self, *args, **kwargs):
        form = super(AuctionUpdateView, self).get_form(*args, **kwargs)
        form.fields['description'].widget = Textarea(attrs={'class': 'form-control', 'rows': 5})
        return form

    def get_success_url(self):
        messages.success(self.request, "Description update succesfully.")
        return reverse('auction-details', kwargs={'pk': self.get_object().pk})


class AuctionBanView(View):
    """
    A view that is used by admins to ban auctions.
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404()

        auction_id = kwargs['pk']
        try:
            obj = Item.objects.get(pk=auction_id)
        except Item.DoesNotExist:
            raise Http404()

        if obj.status == 'DU' or obj.status == "AD":
            raise Http404()

        if obj.status == 'BN':
            obj.status = 'AC'  # AC is the status for active.
            obj.save()
            messages.info(request, 'Auction #{} was unbanned.'.format(obj.pk), "success")
            return HttpResponseRedirect(reverse('main-page'))

        obj.status = 'BN'  # BN is the status for banned.
        obj.save()
        messages.info(request, 'Auction #{} was banned.'.format(obj.pk), "danger")
        return HttpResponseRedirect(reverse('main-page'))


class BannedListView(ListView):
    template_name="auction_site/banned_list.html"
    model=Item

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404()
        else:
            return super(BannedListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(BannedListView, self).get_queryset()
        qs = qs.filter(status="BN")
        return qs
