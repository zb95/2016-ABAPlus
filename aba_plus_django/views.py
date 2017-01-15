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

from django.views import generic
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import json

from abap_parser import *
from aspartix_interface import *

SOLVER_INPUT = "input_for_solver.lp"
TURNSTILE = "&#x22a2;"
R_ARROW = "&rarr;"
L_ARROW = "&larr;"
OVERLINE = "<span style=\"text-decoration: overline\">{}</span>"

BOTH_ATTACKS = 3

STABLE = 1
GROUNDED = 2
COMPLETE = 3
PREFERRED = 4
IDEAL = 5

extension_type_names = {STABLE: "stable", GROUNDED: "grounded",
                      COMPLETE: "complete", PREFERRED: "preferred", IDEAL: "ideal"}

attack_type_names = {NORMAL_ATK: "normal attack", REVERSE_ATK: "reverse attack", BOTH_ATTACKS: "both attacks"}

NOT_HIGHLIGHTED1 = 1
NOT_HIGHLIGHTED2 = 2
HIGHLIGHTED = 3

#maps session keys to calculation results
results = {}

class IndexView(generic.ListView):
    template_name = 'aba_plus_django/index.html'

    def get_queryset(self):
        return None

    def post(self, request, **kwargs):
        if "submit_text" in request.POST:
            request.session['input'] = request.POST['input_text']

        elif "submit_file" in request.POST:
            file = request.FILES['myfile']
            str = ""
            for chunk in file.chunks():
                str += chunk.decode("utf-8")
            request.session['input'] = str

        request.session['auto_WCP'] = False
        request.session['to_compute'] = True

        return HttpResponseRedirect(reverse('aba_plus_django:results'))

class ResultsView(generic.ListView):
    template_name = 'aba_plus_django/results.html'
    context_object_name = 'input'

    def get_queryset(self):
        return self.request.session['input'].replace("\r", "<br/>")

    def get_context_data(self, **kwargs):
        context = super(generic.ListView, self).get_context_data(**kwargs)

        if self.request.session['to_compute']:

            rules_added = None
            res = generate_aba_plus_framework(self.request.session['input'])
            abap = res[0]
            #reverse dictionary to map sentences to contraries
            contr_map = dict((v, k) for k, v in res[1].items())
            if self.request.session['auto_WCP']:
                rules_added = rules_to_str(abap.check_or_auto_WCP(auto_WCP = True), contr_map)
                context['rules_added'] = rules_added
            else:
                abap.check_or_auto_WCP()

            res = abap.generate_arguments_and_attacks_for_contraries()
            attacks = res[1]
            deductions = res[2]

            set_attacks = convert_to_attacks_between_sets(res[1])
            context['attacks'] = [set_atk_to_str(atk) for atk in set_attacks]

            asp = ASPARTIX_Interface(abap)
            asp.generate_input_file_for_clingo(SOLVER_INPUT)

            stable_ext = asp.calculate_stable_arguments_extensions(SOLVER_INPUT)
            grounded_ext = asp.calculate_grounded_arguments_extensions(SOLVER_INPUT)
            complete_ext = asp.calculate_complete_arguments_extensions(SOLVER_INPUT)
            preferred_ext = asp.calculate_preferred_arguments_extensions(SOLVER_INPUT)
            ideal_ext = asp.calculate_ideal_arguments_extensions(SOLVER_INPUT)

            context['stable'] = arguments_extensions_to_str_list(stable_ext, contr_map)
            context['grounded'] = arguments_extensions_to_str_list(grounded_ext, contr_map)
            context['complete'] = arguments_extensions_to_str_list(complete_ext, contr_map)
            context['preferred'] = arguments_extensions_to_str_list(preferred_ext, contr_map)
            context['ideal'] = arguments_extensions_to_str_list(ideal_ext, contr_map)

            # maps indices to extensions
            extension_map = {}
            i = 1
            for ext, conclusions in stable_ext.items():
                extension_map[i] = (ext, conclusions, STABLE)
                i += 1
            for ext, conclusions in grounded_ext.items():
                extension_map[i] = (ext, conclusions, GROUNDED)
                i += 1
            for ext, conclusions in complete_ext.items():
                extension_map[i] = (ext, conclusions, COMPLETE)
                i += 1
            for ext, conclusions in preferred_ext.items():
                extension_map[i] = (ext, conclusions, PREFERRED)
                i += 1
            for ext, conclusions in ideal_ext.items():
                extension_map[i] = (ext, conclusions, IDEAL)
                i += 1
            context['extensions'] = extension_map

            context['json_input'] = generate_json(deductions, attacks, None)

            context['input_text'] = self.request.session['input']

            self.request.session['to_compute'] = False
            self.request.session['highlight_index'] = None
            self.request.session['compare_index'] = None

            results[self.request.session.session_key] = {'abap': abap, 'deductions': deductions, 'attacks': attacks,
                                                         'contr_map': contr_map, 'extension_map': extension_map,
                                                         'stable_ext': stable_ext,
                                                         'grounded_ext': grounded_ext, 'complete_ext': complete_ext,
                                                         'ideal_ext': ideal_ext, 'preferred_ext': preferred_ext,
                                                         'rules_added': rules_added}

        else:
            result = results[self.request.session.session_key]

            context['rules_added'] = result['rules_added']

            set_attacks = convert_to_attacks_between_sets(result['attacks'])
            context['attacks'] = [set_atk_to_str(atk) for atk in set_attacks]

            contr_map = result['contr_map']

            context['stable'] = arguments_extensions_to_str_list(result['stable_ext'], contr_map)
            context['grounded'] = arguments_extensions_to_str_list(result['grounded_ext'], contr_map)
            context['complete'] = arguments_extensions_to_str_list(result['complete_ext'], contr_map)
            context['preferred'] = arguments_extensions_to_str_list(result['preferred_ext'], contr_map)
            context['ideal'] = arguments_extensions_to_str_list(result['ideal_ext'], contr_map)

            highlighted_ext = None
            if  self.request.session['highlight_index']:
                extension_map = result['extension_map']
                to_highlight = self.request.session['highlight_index']
                highlighted_ext = extension_map[to_highlight][0]

                context['highlighted_extension'] = argument_to_str(extension_map[to_highlight][0],
                                                                   extension_map[to_highlight][1], contr_map)
                extension_type = extension_map[to_highlight][2]
                context['highlighted_extension_type'] = extension_type_names[extension_type]

            context['json_input'] = generate_json(result['deductions'], result['attacks'], highlighted_ext)

            if self.request.session['compare_index']:
                extension_map = result['extension_map']
                to_highlight = self.request.session['compare_index']
                highlighted_ext2 = extension_map[to_highlight][0]

                context['compared_extension'] = argument_to_str(extension_map[to_highlight][0],
                                                                   extension_map[to_highlight][1], contr_map)
                extension_type = extension_map[to_highlight][2]
                context['compared_extension_type'] = extension_type_names[extension_type]

                context['render_graph2'] = True
                context['json_input2'] = generate_json(result['deductions'], result['attacks'], highlighted_ext2)

            context['extensions'] = result['extension_map']
            context['input_text'] = self.request.session['input']

        return context

    def post(self, request, **kwargs):
        if "submit_text" in request.POST:
            request.session['input'] = request.POST['input_text']

            request.session['to_compute'] = True
            request.session['auto_WCP'] = False

        elif "submit_file" in request.POST:
            file = request.FILES['myfile']
            str = ""
            for chunk in file.chunks():
                str += chunk.decode("utf-8")
            request.session['input'] = str

            request.session['to_compute'] = True
            request.session['auto_WCP'] = False

        if 'auto_WCP' in self.request.POST:
            self.request.session['auto_WCP'] = True

        elif 'select_extension' in self.request.POST:
            selection = request.POST['select_extension']
            self.request.session['highlight_index'] = int(selection)

        elif 'compare_extension' in self.request.POST:
            selection = request.POST['compare_extension']
            self.request.session['compare_index'] = int(selection)

        return HttpResponseRedirect(reverse('aba_plus_django:results'))



def sets_to_str(sets, contr_map={}):
    """
    :param sets: set of sets of Sentences to format
    :param contr_map: dictionary mapping symbols of contraries to symbols of assumptions (default empty)
    :return: formatted string representation of sets
    """
    str = ""

    it = iter(sets)
    first_set = next(it, None)
    if first_set is not None:
        str += set_to_str(first_set, contr_map)
    for set in it:
        str += ", "
        str += set_to_str(set, contr_map)

    return str

def set_to_str(set, contr_map={}):
    """
    :param set: set of Sentences to format
    :param contr_map: dictionary mapping symbols of contraries to symbols of assumptions (default empty)
    :return: formatted string representation of sets
    """
    str = "{"

    it = iter(set)
    first_sentence = next(it, None)
    if first_sentence is not None:
        str += sentence_to_str(first_sentence, contr_map)
    for sentence in it:
        str += ", "
        str += sentence_to_str(sentence, contr_map)

    str += "}"

    return str

def sentence_to_str(sentence, contr_map={}):
    """
    :param sentence: Sentence to format
    :param contr_map: dictionary mapping symbols of contraries to symbols of assumptions (default empty)
    :return: formatted string representation of sentence
    """
    if sentence.is_contrary:
        if sentence.symbol in contr_map:
            return contr_map[sentence.symbol]
        return OVERLINE.format(sentence.symbol)
    else:
        return sentence.symbol

def set_atk_to_str(atk):
    """
    :param atk: tuple with 3 elements representing an attack between 2 sets:
                1: attacking set of Sentences
                2: attack type
                3: attacked set of Sentences
    :return: formatted string representation of atk
    """
    str = ""

    type = atk[2]
    if type == NORMAL_ATK:
        str = "Normal Attack: "
    elif type == REVERSE_ATK:
        str = "Reverse Attack: "

    str += set_to_str(atk[0])
    str += " {} ".format(R_ARROW)
    str += set_to_str(atk[1])

    return str

def arguments_extensions_to_str_list(extensions_dict, contr_map={}):
    """
    :param extensions_dict: dictionary mapping sets to their conclusions
    :param contr_map: dictionary mapping symbols of contraries to symbols of assumptions (default empty)
    :return: list of formatted arguments(deductions)
    """
    res = []

    for extension, conclusions in extensions_dict.items():
        res.append(argument_to_str(extension, conclusions, contr_map))

    return res

def argument_to_str(premise, conclusion, contr_map={}):
    """
    :param premise: set of Sentences representing the premise
    :param conclusion: set of Sentences representing the conclusion
    :param contr_map: dictionary mapping symbols of contraries to symbols of assumptions (default empty)
    :return: formatted argument(deduction)
    """
    str = ""
    str += set_to_str(premise)
    str += " {} ".format(TURNSTILE)
    str += set_to_str(conclusion, contr_map)
    return str

def rules_to_str(rules, contr_map):
    """
    :param rules: collection of Rules to format
    :param contr_map: dictionary mapping symbols of contraries to symbols of assumptions (default empty)
    :return: formatted string representation of rules
    """
    str = ""

    for rule in rules:
        str += rule_to_str(rule, contr_map)

    return str

def rule_to_str(rule, contr_map):
    """
    :param rule: Rule to format
    :param contr_map: dictionary mapping symbols of contraries to symbols of assumptions (default empty)
    :return: formatted string representation of rule
    """
    str = ""

    str += sentence_to_str(rule.consequent, contr_map)
    str += " {} ".format(L_ARROW)
    str += set_to_str(rule.antecedent)

    str += "<br/>"

    return str


def generate_json(deductions, attacks, highlighted_sentences):
    """
    generate a json file with nodes and links representing sets and attacks between them
    :param deductions: collection of Deductions whose premises are to be represented as nodes
    :param attacks: collection of Attacks to be represented as directed links
    :param highlighted_sentences: collection of Sentences to be highlighted
    :return: string containing the the json
    """
    output = {"nodes": list(), "links": list()}

    support_sets = []
    for ded in deductions:
        if ded.premise not in support_sets:
            support_sets.append(ded.premise)

            if not(highlighted_sentences is None):
                group = HIGHLIGHTED if frozenset(ded.premise).issubset(highlighted_sentences) else NOT_HIGHLIGHTED2
            else:
                group = NOT_HIGHLIGHTED1

            node = {"name": set_to_str(ded.premise),
                    "group": group}
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


