from django.forms import ModelForm

from auction.models import Bid


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['user', 'price', 'auction']
