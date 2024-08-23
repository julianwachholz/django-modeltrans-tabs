# django-modeltrans-tabs

Add a tabbed UI to `django-modeltrans` translation fields in the Django Admin.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="img/modeltrans_tabs_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="img/modeltrans_tabs_light.png">
  <img alt="Tabbed translation admin UI." src="img/modeltrans_tabs_light.png">
</picture>

## Installation

Use your preferred package manager:

```bash
pip install django-modeltrans-tabs
```

## Setup

Just two steps to enable. First, update your `settings.py`:

```py
INSTALLED_APPS = [
    # Ensure staticfiles is installed
    "django.contrib.staticfiles",
    #
    # Add modeltrans-tabs:
    "modeltrans_tabs",
]
```

Then, inherit the mixin from your `ModelAdmin`:

```py
from modeltrans_tabs.admin import TabbedLanguageMixin


class MyModelAdmin(TabbedLanguageMixin, admin.ModelAdmin):
    ...

```
