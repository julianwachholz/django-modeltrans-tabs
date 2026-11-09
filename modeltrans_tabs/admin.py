from django.conf import settings
from modeltrans.conf import get_default_language
from modeltrans.fields import TranslatedVirtualField
from modeltrans.translator import get_i18n_field


def get_languages():
    """The languages in the order of MODELTRANS_AVAILABLE_LANGUAGES, or of LANGUAGES when that
    isn't set, which is what modeltrans uses too. The default language comes first if neither
    lists it (modeltrans always has it: it's the original field)."""
    configured = getattr(settings, "MODELTRANS_AVAILABLE_LANGUAGES", None)
    if configured is None:
        configured = [code for code, _name in settings.LANGUAGES]
    languages = list(dict.fromkeys(configured))
    default = get_default_language()
    if default not in languages:
        languages.insert(0, default)
    return languages


def sort_by_language(fields):
    """Translated fields in the configured language order (see get_languages)."""
    languages = get_languages()

    def position(field):
        try:
            return languages.index(field.language)
        except ValueError:
            return len(languages)  # not configured: last, in their own order

    return sorted(fields, key=position)


class TabbedLanguageMixin:
    """ModelAdmin mixin to giving access to all languages for each i18n field using tabs."""

    class Media:
        css = {
            "all": ("modeltrans_tabs/i18n_tabs.css",),
        }
        js = ("modeltrans_tabs/i18n_tabs.js",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._i18n_field = get_i18n_field(self.model)

    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if self._i18n_field is None:
            return field

        if isinstance(db_field, TranslatedVirtualField):
            field.widget.attrs["data-i18n-lang"] = db_field.language or ""
            field.widget.attrs["data-i18n-field"] = db_field.original_name
            if not db_field.language:
                field.widget.attrs["required"] = not db_field.original_field.blank
            elif db_field.language == get_default_language():
                field.widget.attrs["data-i18n-default"] = "true"

        return field

    def i18n_field(self, field_name: str):
        fields = [field_name]

        if self._i18n_field is None:
            return fields

        translated = [
            field
            for field in self._i18n_field.get_translated_fields()
            if field.original_name == field_name and field.language is not None
        ]
        fields += [field.name for field in sort_by_language(translated)]
        return tuple(fields)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if self._i18n_field is None or not fieldsets:
            return fieldsets

        fieldsets = list(fieldsets)

        real_to_virtual_fields = {}
        virtual_field_names = set()
        for field in sort_by_language(self._i18n_field.get_translated_fields()):
            virtual_field_names.add(field.name)

            # Remove _i18n fields from fieldsets
            if field.language is None:
                continue

            if field.original_name not in real_to_virtual_fields:
                real_to_virtual_fields[field.original_name] = []
            real_to_virtual_fields[field.original_name].append(field.name)

        translated_fieldsets = []
        for label, fieldset in fieldsets:
            field_names = []
            for field_name in fieldset.get("fields", []):
                if field_name in real_to_virtual_fields:
                    field_names.append(
                        [field_name] + real_to_virtual_fields[field_name]
                    )

                elif field_name not in virtual_field_names:
                    field_names.append(field_name)

            new_fieldset = {
                "fields": field_names,
                "classes": fieldset.get("classes", []),
            }
            translated_fieldsets.append((label, new_fieldset))

        return translated_fieldsets
