from aba_plus_ import *
from django.http import HttpResponse

class ExceptionMiddleware(object):
    def process_exception(self, request, exception, *args, **kwargs):
        if isinstance(exception, CyclicPreferenceException) or \
           isinstance(exception, NonFlatException):
            return HttpResponse(exception.message)
        return None