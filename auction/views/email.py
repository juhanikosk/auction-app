from os import listdir

from django.core import mail
from django.http import HttpResponse, Http404
from django.views import View
from django.shortcuts import render


class EmailListView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404()
        else:
            return super(EmailListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Render the email files to a list.
        """
        emails = mail.get_connection()
        email_array = []
        files = listdir(emails.file_path)
        for f in files:
            with open("{}/{}".format(emails.file_path,f), 'r') as static_file:
                email_array.append([mail_line for mail_line in static_file.read().split('\n')])
        return render(request, "email/email_list.html", {'email_list': email_array})
