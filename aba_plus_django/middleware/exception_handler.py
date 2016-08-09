from aba_plus_ import *
from django.http import HttpResponse

class ExceptionMiddleware(object):
    def process_exception(self, request, exception, *args, **kwargs):
        if isinstance(exception, CyclicPreferenceException):
            return HttpResponse('Cycle in preferences detected!')
        return None