__author__ = "Ziyi Bao"
__email__ = "zb714@ic.ac.uk"
__copyright__ = "Copyright (c) 2016 Ziyi Bao"

from django import template
from aba_plus_django.views import *

register = template.Library()
TURNSTILE = "&#x22a2;"

@register.filter(name='f_deduction')
def format_deduction(deduction):
    str = ""
    str += set_to_str(deduction.premise)
    str += " {} ".format(TURNSTILE)
    str += set_to_str(deduction.conclusion)
    return str

@register.filter(name='f_set')
def format_set(set_to_format):
    return set_to_str(set_to_format)
