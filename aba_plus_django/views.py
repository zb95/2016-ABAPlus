from django.views import generic
from django.http import HttpResponseRedirect

class IndexView(generic.ListView):
    template_name = 'aba_plus_django/index.html'

    def get_queryset(self):
        return None

    def post(self, request):
        file = request.FILES['myfile']
        str = ""
        for chunk in file.chunks():
            str += chunk.decode("utf-8")
        print(str)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))