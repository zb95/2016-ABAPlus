from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
import requests
import json

from aba_plus_ import *
from abap_parser import *
from aspartix_interface import *

SOLVER_INPUT = "input_for_solver.lp"
TURNSTILE = "&#x22a2;"
ARROW = "&rarr;"
OVERLINE = "<span style=\"text-decoration: overline\">{}</span>"
BOTH_ATTACKS = 3

class IndexView(generic.ListView):
    template_name = 'aba_plus_django/index.html'

    def get_queryset(self):
        return None

    def post(self, request, **kwargs):
        file = request.FILES['myfile']
        str = ""
        for chunk in file.chunks():
            str += chunk.decode("utf-8")
        request.session['input'] = str

        if "auto_WCP" in request.POST:
            request.session['auto_WCP'] = True
        else:
            request.session['auto_WCP'] = False
        '''
        try:
            request.session['abap'] = generate_aba_plus_framework(self.request.session['input'])
        except CyclicPreferenceException:
            return render(self.request, template_name='aba_plus_django/error_msg.html', context={'message': 'Cycle in preferences detected!'})
        else:
            return HttpResponseRedirect(reverse('aba_plus_django:results'))
        '''
        return HttpResponseRedirect(reverse('aba_plus_django:results'))

class ResultsView(generic.ListView):
    template_name = 'aba_plus_django/results.html'
    context_object_name = 'input'

    def get_queryset(self):
        return self.request.session['input'].replace("\r", "<br/>")

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)

        if self.request.session['auto_WCP']:
            abap = generate_aba_plus_framework(self.request.session['input'])
            context['rules_added'] = rules_to_str(abap.check_or_auto_WCP(auto_WCP = True))
        else:
            abap = generate_aba_plus_framework(self.request.session['input'])
            abap.check_or_auto_WCP()

        res = abap.generate_arguments_and_attacks_for_contraries()


        context['json_input'] = generate_json(res[2], res[1])
        print(generate_json(res[2], res[1]))

        set_attacks = convert_to_attacks_between_sets(res[1])
        context['attacks'] = [set_atk_to_str(atk) for atk in set_attacks]

        '''
        print(self.request.session['auto_WCP'])
        if self.request.session['auto_WCP']:
            rules_added = abap.check_and_partially_satisfy_WCP()
            if rules_added:
                context['rules_added'] = rules_to_str(rules_added)
            else:
                context['WCP'] = "The Weak Contraposition is fulfilled"
        else:
            WCP_fulfilled = abap.check_WCP()
            if WCP_fulfilled:
                print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
                context['WCP'] = "The Weak Contraposition is fulfilled"
            else:
                print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")
                context['WCP'] = "The Weak Contraposition is not fulfilled"
        '''

        asp = ASPARTIX_Interface(abap)
        asp.generate_input_file_for_clingo(SOLVER_INPUT)
        context['stable'] = arguments_extensions_to_str(asp.calculate_stable_arguments_extensions(SOLVER_INPUT))
        context['grounded'] = arguments_extensions_to_str(asp.calculate_grounded_arguments_extensions(SOLVER_INPUT))
        context['complete'] = arguments_extensions_to_str(asp.calculate_complete_arguments_extensions(SOLVER_INPUT))
        context['preferred'] = arguments_extensions_to_str(asp.calculate_preferred_arguments_extensions(SOLVER_INPUT))
        context['ideal'] = arguments_extensions_to_str(asp.calculate_ideal_arguments_extensions(SOLVER_INPUT))

        return context

    def post(self, request, **kwargs):
        if 'auto_WCP' in self.request.POST:
            print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
            self.request.session['auto_WCP'] = True
        return HttpResponseRedirect(reverse('aba_plus_django:results'))



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
        str += sentence_to_str(first_sentence)
    for sentence in it:
        str += ", "
        str += sentence_to_str(sentence)

    str += "}"

    return str

def sentence_to_str(sentence):
    if sentence.is_contrary:
        return OVERLINE.format(sentence.symbol)
    else:
        return sentence.symbol

def set_atk_to_str(atk):
    str = ""

    type = atk[2]
    if type == NORMAL_ATK:
        str = "Normal Attack: "
    elif type == REVERSE_ATK:
        str = "Reverse Attack: "

    str += set_to_str(atk[0])
    str += " {} ".format(ARROW)
    str += set_to_str(atk[1])

    return str

def arguments_extensions_to_str(extensions_dict):
    str = ""

    for extension, conclusions in extensions_dict.items():
        str += set_to_str(extension)
        str += " {} ".format(TURNSTILE)
        str += set_to_str(conclusions)
        str += "<br/>"

    return str

def rules_to_str(rules):
    str = ""

    for rule in rules:
        str += rule_to_str(rule)

    return str

def rule_to_str(rule):
    str = ""

    str += set_to_str(rule.antecedent)
    str += " {} ".format(ARROW)
    str += sentence_to_str(rule.consequent)
    str += "<br/>"

    return str


def generate_json(deductions, attacks):
    output = {"nodes": list(), "links": list()}

    support_sets = []
    for ded in deductions:
        if ded.premise not in support_sets:
            support_sets.append(ded.premise)

            node = {"name": set_to_str(ded.premise),
                    "group": 1}
            output["nodes"].append(node)

    # maps (attacker, attackee) to attack type
    attack_map = {}
    for atk in attacks:
        key = (frozenset(atk.attacker.premise), frozenset(atk.attackee.premise))
        if key not in attack_map:
            attack_map[key] = atk.type
        elif atk.type != attack_map[key]:
            attack_map[key] = BOTH_ATTACKS

    for k, v in attack_map.items():
        idx_attacker = support_sets.index(k[0])
        idx_attackee = support_sets.index(k[1])

        link = {"source": idx_attacker,
                "target": idx_attackee,
                "value": v}
        output["links"].append(link)

    return json.dumps(output)


