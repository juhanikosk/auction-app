from django.db import models


class NewsItem(models.Model):
    """
    Represents a news item that can be seen in the main page.
    """
    class Meta:
        app_label="auction"

    title = models.CharField(blank=False, max_length=255)
    description = models.CharField(blank=False, max_length=255)
    text = models.CharField(blank=False, max_length=2048)
