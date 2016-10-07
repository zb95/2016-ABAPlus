__author__ = "Ziyi Bao"
__email__ = "zb714@ic.ac.uk"
__copyright__ = "Copyright (c) 2016 Ziyi Bao"

from abap_parser import *
from django.shortcuts import render

class ExceptionMiddleware(object):
    def process_exception(self, request, exception, *args, **kwargs):
        if isinstance(exception, CyclicPreferenceException) or \
           isinstance(exception, NonFlatException) or \
           isinstance(exception, InvalidPreferenceException) or \
           isinstance(exception, DuplicateSymbolException) or \
           isinstance(exception, InvalidContraryDeclarationException) or \
           isinstance(exception, InvalidPreferenceDeclarationException):
            return render(request, template_name='../templates/aba_plus_django/error_page.html',
                          context={'msg':exception.message})
        elif isinstance(exception, WCPViolationException):
            return render(request, template_name='../templates/aba_plus_django/auto_wcp.html')
        elif isinstance(exception, KeyError):
            return render(request, template_name='../templates/aba_plus_django/error_page.html',
                          context={'msg': "Session has ended."})
        #else:
           # return HttpResponse("An unknown error has occured.")
        return None