
import base64
from django import template

register = template.Library()

@register.filter
def encrypt_parameter(value):
    return base64.urlsafe_b64encode(str(value).encode()).decode()

@register.filter
def decrypt_parameter(value):
    return int(base64.urlsafe_b64decode(value.encode()).decode())
