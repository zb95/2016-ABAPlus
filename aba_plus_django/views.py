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
        return self.request.session['input'].replace("\r", "<br/>")

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)
        #print(self.request.session['input'])
        abap = generate_aba_plus_framework(self.request.session['input'])
        attacks = convert_to_attacks_between_sets(abap.generate_arguments_and_attacks_for_contraries()[1])
        context['attacks'] = [set_atk_to_str(atk) for atk in attacks]
        asp = ASPARTIX_Interface(abap)
        asp.generate_input_file_for_clingo(SOLVER_INPUT)
        context['stable'] = sets_to_str(asp.calculate_stable_extensions(SOLVER_INPUT))
        context['grounded'] = sets_to_str(asp.calculate_grounded_extensions(SOLVER_INPUT))
        context['complete'] = sets_to_str(asp.calculate_complete_extensions(SOLVER_INPUT))
        context['preferred'] = sets_to_str(asp.calculate_preferred_extensions(SOLVER_INPUT))
        context['ideal'] = sets_to_str(asp.calculate_ideal_extensions(SOLVER_INPUT))

        return context

def sets_to_str(sets):
    str = ""

    it = iter(sets)
    first_set = next(it, None)
    if first_set is not None:
        str += set_to_str(first_set)
    for set in it:
        str += ", "
        str += set_to_str(set)

    return str

def set_to_str(set):
    str = "{"

    it = iter(set)
    first_sentence = next(it, None)
    if first_sentence is not None:
        str += first_sentence.symbol
    for sentence in it:
        str += ", "
        str += sentence.symbol

    str += "}"

    return str

def set_atk_to_str(atk):
    str = ""

    type = atk[2]
    if type == NORMAL_ATK:
        str = "Normal Attack: "
    elif type == REVERSE_ATK:
        str = "Reverse Attack: "

    str += set_to_str(atk[0])
    str += " -> "
    str += set_to_str(atk[1])

    return str



