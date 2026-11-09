from django.contrib import admin
from django.test import RequestFactory

from modeltrans_tabs.admin import TabbedLanguageMixin, get_languages

from .models import Page


class PageAdmin(TabbedLanguageMixin, admin.ModelAdmin):
    pass


class FieldsetsPageAdmin(TabbedLanguageMixin, admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["slug", "title", "body"]})]


def fields(admin_class):
    model_admin = admin_class(Page, admin.site)
    fieldsets = model_admin.get_fieldsets(RequestFactory().get("/"))
    return [
        tuple(field) if isinstance(field, list) else field
        for field in fieldsets[0][1]["fields"]
    ]


def test_tabs_follow_languages():
    assert get_languages() == ["en", "fr", "de", "it"]
    assert fields(FieldsetsPageAdmin) == [
        "slug",
        ("title", "title_en", "title_fr", "title_de", "title_it"),
        ("body", "body_en", "body_fr", "body_de", "body_it"),
    ]


def test_tabs_follow_modeltrans_available_languages(settings):
    settings.MODELTRANS_AVAILABLE_LANGUAGES = ["de", "en", "it", "fr"]
    assert get_languages() == ["de", "en", "it", "fr"]
    assert fields(FieldsetsPageAdmin)[1] == (
        "title",
        "title_de",
        "title_en",
        "title_it",
        "title_fr",
    )


def test_the_default_language_comes_first_when_not_listed(settings):
    settings.MODELTRANS_AVAILABLE_LANGUAGES = ["it", "de"]
    assert get_languages() == ["en", "it", "de"]


def test_default_fieldsets_and_the_helper_use_the_same_order():
    assert ("title", "title_en", "title_fr", "title_de", "title_it") in fields(
        PageAdmin
    )
    model_admin = PageAdmin(Page, admin.site)
    assert model_admin.i18n_field("body") == (
        "body",
        "body_en",
        "body_fr",
        "body_de",
        "body_it",
    )
