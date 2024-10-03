from modeltrans.conf import get_default_language
from modeltrans.fields import TranslatedVirtualField
from modeltrans.translator import get_i18n_field


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

        for field in self._i18n_field.get_translated_fields():
            if field.original_name == field_name and field.language is not None:
                fields.append(field.name)
        return tuple(fields)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if self._i18n_field is None or not fieldsets:
            return fieldsets

        fieldsets = list(fieldsets)

        real_to_virtual_fields = {}
        virtual_field_names = set()
        for field in self._i18n_field.get_translated_fields():
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
                        [field_name] + sorted(real_to_virtual_fields[field_name])
                    )

                elif field_name not in virtual_field_names:
                    field_names.append(field_name)

            new_fieldset = {
                "fields": field_names,
                "classes": fieldset.get("classes", []),
            }
            translated_fieldsets.append((label, new_fieldset))

        return translated_fieldsets
