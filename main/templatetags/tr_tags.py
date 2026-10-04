from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from main.translations import get_text

register = template.Library()


@register.simple_tag
def tr(key, **kwargs):
    """
    {% tr 'submit' %}
    {% tr 'locked_by' sender=name recipient=name2 %}
    O'zgaruvchilar HTML-escape qilinadi (XSS himoyasi).
    """
    text = get_text(key)
    if not kwargs:
        return text
    safe_values = {k: format_html('<b>{}</b>', v) for k, v in kwargs.items()}
    return mark_safe(text.format(**safe_values))