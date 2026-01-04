import re
from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter
def highlight(text,search):
    if search not in text:
        return text
    
    pattern = re.compile(re.escape(search),re.IGNORECASE)

    highlighted = pattern.sub(
        lambda m : f"<mark>{m.group(0)}</mark>",
        search
    )

    return mark_safe(highlighted)