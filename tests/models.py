from django.db import models
from modeltrans.fields import TranslationField


class Page(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(blank=True)
    slug = models.SlugField()
    i18n = TranslationField(fields=["title", "body"])

    class Meta:
        app_label = "tests"
