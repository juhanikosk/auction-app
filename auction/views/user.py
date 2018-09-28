from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import DetailView, UpdateView, FormView


from auction.models import AuctionUser


class UserUpdateView(UpdateView):
    model=AuctionUser
    template_name="user/edit_details.html"
    fields=['username', 'email', 'first_name', 'last_name', 'phone']

    def get_queryset(self):
        return AuctionUser.objects.filter(pk=self.request.user.pk)

    def get_success_url(self):
        messages.success(self.request, "User information saved succesfully.")
        return reverse('user-detail-view', kwargs={'pk': self.request.user.pk})


class UserDetailView(DetailView):
    model=AuctionUser
    template_name="user/show_details.html"


class UserPasswordView(FormView):
    model=AuctionUser
    template_name="user/edit_details.html"
    form_class=PasswordChangeForm

    def get_success_url(self):
        return reverse('main-page')

    def get_form(self):
        form = PasswordChangeForm(self.request.user)
        return form

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
        else:
            messages.info(request, form.errors, 'danger')

        return super(UserPasswordView, self).post(request, *args, **kwargs)
