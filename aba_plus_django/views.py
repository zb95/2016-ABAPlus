from django.views import generic
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import requests

from aba_plus_ import *
from abap_parser import *
from aspartix_interface import *

SOLVER_INPUT = "input_for_solver.lp"

class IndexView(generic.ListView):
    template_name = 'aba_plus_django/index.html'

    def get_queryset(self):
        return None

    def post(self, request):
        file = request.FILES['myfile']
        str = ""
        for chunk in file.chunks():
            str += chunk.decode("utf-8")
        request.session['input'] = str
        return HttpResponseRedirect(reverse('aba_plus_django:results'))

class ResultsView(generic.ListView):
    template_name = 'aba_plus_django/results.html'
    context_object_name = 'input'

    def get_queryset(self):
        return self.request.session['input']

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        #print(self.request.session['input'])
        abap = generate_aba_plus_framework(self.request.session['input'])
        print(len(abap.assumptions))
        asp = ASPARTIX_Interface(abap)
        asp.generate_input_file_for_clingo(SOLVER_INPUT)
        stable_ext = asp.calculate_stable_extensions(SOLVER_INPUT)
        print(stable_ext)
        context['stable'] = list()
        for set in stable_ext:
            symbols = [sentence.symbol for sentence in set]
            print(symbols)
            context['stable'].append(symbols)
        context['grounded'] = asp.calculate_grounded_extensions(SOLVER_INPUT)
        context['complete'] = asp.calculate_complete_extensions(SOLVER_INPUT)
        context['preferred'] = asp.calculate_preferred_extensions(SOLVER_INPUT)
        context['ideal'] = asp.calculate_ideal_extensions(SOLVER_INPUT)

        return context
