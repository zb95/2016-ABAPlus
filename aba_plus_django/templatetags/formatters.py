"""Copyright 2017 Ziyi Bao, Department of Computing, Imperial College London

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

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
