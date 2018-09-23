from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import DetailView, UpdateView


from auction.models import AuctionUser


class UserUpdateView(UpdateView):
    model=AuctionUser
    template_name="user/edit_details.html"
    fields=['username', 'email', 'first_name', 'last_name', 'phone']

    def get_success_url(self):
        return reverse('user-detail-view', kwargs={'pk': self.request.user.pk})


class UserDetailView(DetailView):
    model=AuctionUser
    template_name="user/show_details.html"
