from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.shortcuts import render


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "main.html")
