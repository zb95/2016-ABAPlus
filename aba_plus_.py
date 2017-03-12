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

"""
This module contains a class ABA_Plus that represents an ABA+ framework as well as other classes to represent
different components of such framework (assumptions, rules and preferences).
"""

import numpy as np
import functools as ft

LESS_THAN = 1
LESS_EQUAL = 2
NO_RELATION = 3

CANNOT_BE_DERIVED = -1

NORMAL_ATK = 1
REVERSE_ATK = 2

class ABA_Plus:
    def __init__(self, assumptions, preferences, rules):
        """
        :param assumptions: set of Sentences
        :param preferences: set of Preferences
        :param rules: set of Rules
        """
        self.assumptions = assumptions
        self.preferences = preferences
        self.rules = rules

        if not self.is_flat():
            raise NonFlatException("The framework is not flat!")

        if not self.preferences_only_between_assumptions():
            raise InvalidPreferenceException("Non-assumption in preference detected!")

        if not self.calc_transitive_closure():
            raise CyclicPreferenceException("Cycle in preferences detected!")

    def __str__(self):
        return str(self.__dict__)

    def check_or_auto_WCP(self, **kwargs):
        """
        Check WCP is satisfied
        If arg auto_WCP is True, automatically satisfy WCP
        :return: the set of rules added to satisfy WCP if auto_WCP == True, otherwise return None

        """
        auto_WCP = kwargs.get('auto_WCP', False)

        if auto_WCP:
            return self.check_and_partially_satisfy_WCP()
        elif not self.check_WCP():
            raise WCPViolationException("Weak Contraposition is not satisfied!")

        return None

    def is_flat(self):
        """
        Check if ABA+ framework is flat
        :return: True if framework is flat, False otherwise
        """
        for rule in self.rules:
            if rule.consequent in self.assumptions:
                return False

        return True

    def preferences_only_between_assumptions(self):
        """
        Check if preference relations are only between assumptoins
        :return: True if the above is true, False otherwise
        """
        for pref in self.preferences:
            if pref.assump1 not in self.assumptions or \
               pref.assump2 not in self.assumptions:
                return False
        return True

    def calc_transitive_closure(self):
        """
        Calculate transitive closure of preference relations
        Add the result of calculation to the framework, if no error occurs
        :return: True if no cycle in preference relations is detected, False otherwise
        """
        assump_list = list(self.assumptions)
        m = len(assump_list)
        relation_matrix = np.full((m, m), NO_RELATION)
        np.fill_diagonal(relation_matrix, LESS_EQUAL)
        for pref in self.preferences:
            idx1 = assump_list.index(pref.assump1)
            idx2 = assump_list.index(pref.assump2)
            relation_matrix[idx1][idx2] = pref.relation

        closed_matrix = self._transitive_closure(relation_matrix)

        for i in range(0, m):
            for j in range(0, m):
                relation = closed_matrix[i][j]
                # cycle detected
                if i == j and relation == LESS_THAN:
                    return False
                if i != j and relation != NO_RELATION:
                    assump1 = assump_list[i]
                    assump2 = assump_list[j]
                    self.preferences.add(Preference(assump1, assump2, relation))

        return True

    def _transitive_closure(self, relation_matrix):
        """
        Calculate transitive closure given a relation matrix
        :param relation_matrix: relation matrix, where LESS_THAN represents < and LESS_EQUAL represents <=
        :return: a relation matrix of the transitive closure
        """
        n = len(relation_matrix)
        d = np.copy(relation_matrix)

        for k in range(0, n):
            for i in range(0, n):
                for j in range(0, n):
                    alt_rel = NO_RELATION
                    if not (d[i][k] == NO_RELATION or d[k][j] == NO_RELATION):
                        alt_rel = min(d[i][k], d[k][j])

                    d[i][j] = min(d[i][j], alt_rel)

        return d

    def deriving_rules(self, sentence):
        """
        :return: the set of all rules deriving sentence
        """
        der_rules = set()
        for rule in self.rules:
            if rule.consequent == sentence:
                der_rules.add(rule)
        return der_rules


    def get_relation(self, assump1, assump2):
        """
        :return: the strongest relation between two assumptions, assump1 and assump2
        """
        strongest_relation_found = NO_RELATION
        for pref in self.preferences:
            if pref.assump1 == assump1 and pref.assump2 == assump2 and \
               pref.relation < strongest_relation_found:
                strongest_relation_found = pref.relation
        return strongest_relation_found

    def is_preferred(self, assump1, assump2):
        """
        :return: True if the relation assump2 < assump1 exists, False otherwise
        """
        return self.get_relation(assump2, assump1) == LESS_THAN


    def deduction_exists(self, to_deduce, deduce_from):
        """
        :param to_deduce: a Sentence
        :param deduce_from: set of Sentences
        :return: True, if to_deduce can be deduced from deduce_from
        """
        rules_applied = set()
        deduced = deduce_from.copy()
        new_rule_used = True
        while new_rule_used:
            new_rule_used = False
            for rule in self.rules:
                if rule not in rules_applied:
                    if rule.antecedent.issubset(deduced):
                        new_rule_used = True
                        if rule.consequent == to_deduce:
                            return True
                        else:
                            deduced.add(rule.consequent)
                        rules_applied.add(rule)

        return False

    def generate_all_deductions(self, deduce_from):
        """
        :param deduce_from: set of Sentences
        :return: set of all Sentences that can be derived from deduce_from
        """
        rules_applied = set()
        deduced = deduce_from.copy()
        new_rule_used = True
        while new_rule_used:
            new_rule_used = False
            for rule in self.rules:
                if rule not in rules_applied:
                    if rule.antecedent.issubset(deduced):
                        new_rule_used = True
                        deduced.add(rule.consequent)
                        rules_applied.add(rule)

        return deduced

    def set_combinations(self, iterable):
        """
        Compute all combinations of sets of sets
        example:
        set_combinations({{b}},{{e},{f}}) returns {{b,e},{b,f}}
        """
        return self._set_combinations(iter(iterable))

    def _set_combinations(self, iter):
        current_set = next(iter, None)
        if current_set is not None:
            sets_to_combine_with = self._set_combinations(iter)
            resulting_combinations = set()
            for c in current_set:
                if not sets_to_combine_with:
                    resulting_combinations.add(frozenset(c))
                for s in sets_to_combine_with:
                    resulting_combinations.add(frozenset(c.union(s)))

            return resulting_combinations

        return set()


    def check_WCP(self):
        """
        :return: True if WCP is satisfied for the framework, False otherwise
        (check_WCP bug fix by K. Cyras, 01/03/2017)
        """
        for assump in self.assumptions:
            attacker_sets = self.generate_arguments(assump.contrary())
            for attacker_set in attacker_sets:
                culprit_list = [ c for c in set(attacker_set) if self.is_preferred(assump, c)]
                # get a list of "culprits" -- assumptions in attacker_set that are < assump
                culprits = set(culprit_list)
                # put the culprit list into a set
                minimal_culprits = self.set_of_minimal_elements(culprits)
                # get the set of <-minimal culprits
                for attacker in minimal_culprits:
                # for every <-minimal culprit
                    if self._WCP_fulfilled(attacker, assump, set(attacker_set)):
                        # if there is a deduction required for WCP
                        break
                        # then break the loop
                    else:
                        # else, if for no <-minimal cuplrit a deduction required for WCP was found,
                        return False
                        # then WCP is not satisfied

        return True
        # WCP is satisfied in other cases

    def set_of_minimal_elements(self, given_set):
        """
        :return: the set of <-minimal elements of a given set
        (helper function for the check_WCP bug fix by K. Cyras, 01/03/2017)
        """
        minimal = set()
        # initiates minimal to be the empty set
        for c in given_set:
                # for every element c of the given set
                if not self.get_minimally_preferred(c, given_set):
                        # if there is no element in the given set which is < c
                        minimal.add(c)
                        # then c is <-minimal, so add it to the set minimal
        return minimal
        # returns the set of <-minimal elements of the given set


    def check_and_partially_satisfy_WCP(self):
        """
        Add rules to the framework in order to satisfy WCP
        :return: set of rules added to the framework
        """
        rules_added = set()
        for assump in self.assumptions:
            attacker_sets = self.generate_arguments(assump.contrary())
            for attacker_set in attacker_sets:
                for attacker in attacker_set:
                    if self.is_preferred(assump, attacker) and \
                       not self._WCP_fulfilled(attacker, assump, set(attacker_set)):
                        minimally_preferred = self.get_minimally_preferred(assump, attacker_set)
                        new_attacker_set = attacker_set.union({assump}).difference({minimally_preferred})
                        new_rule = Rule(new_attacker_set, minimally_preferred.contrary())
                        self.rules.add(new_rule)
                        rules_added.add(new_rule)
                        break
        return rules_added

    def _WCP_fulfilled(self, contradictor, assumption, antecedent):
        negated_contr = contradictor.contrary()
        deduce_from = antecedent.copy()
        deduce_from.add(assumption)
        deduce_from.remove(contradictor)
        return self.deduction_exists(negated_contr, deduce_from)

    def get_minimally_preferred(self, compare_against, assumptions):
        """
        :param compare_against: assumption which should have higher preference than the return value
        :return: the minimally preferred assumptions in assumptions, which has lower preference than compare_against,
                 return None if none exists
        """
        filtered = [assump for assump in assumptions if self.is_preferred(compare_against, assump)]
        it = iter(filtered)
        minimal = next(it, None)
        for assump in it:
            if self.is_preferred(minimal, assump):
                minimal = assump

        return minimal

    #TODO: rename to avoid confusion between supporting sets and 'arguments' in abstract argumentation
    def generate_arguments(self, generate_for):
        """
        :param generate_for: a Sentence
        :return: set of sets of assumptions, where each set contains assumptions deducing generate_for
        """
        return self._generate_arguments(generate_for, set())

    def _generate_arguments(self, generate_for, rules_seen):
        if generate_for in self.assumptions:
            return {frozenset({generate_for})}

        der_rules = self.deriving_rules(generate_for)
        results = set()
        for rule in der_rules:
            if rule not in rules_seen:
                supporting_assumptions = set()
                args_lacking = False
                if not rule.antecedent:
                    empty_set = set()
                    empty_set.add(frozenset())
                    supporting_assumptions.add(frozenset(empty_set))
                _rules_seen = rules_seen.copy()
                _rules_seen.add(rule)
                for ant in rule.antecedent:
                    args = self._generate_arguments(ant, _rules_seen)
                    if not args:
                        args_lacking = True
                        break
                    supporting_assumptions.add(frozenset(args))

                if not args_lacking:
                    results = results.union(self.set_combinations(supporting_assumptions))
        return results

    def generate_arguments_and_attacks(self, generate_for):
        """
        generate arguments supporting generate_for and all attacks between the arguments
        :param generate_for:
        :return: tuple (deductions, attacks, all_deductions)
                 deductions: dictionary that maps sentences to sets of Deductions that deduce them
                 attacks: set of all attacks generated
                 all_deductions: set of all Deductions generated
        """
        deductions = {}
        attacks = set()
        # maps attackees to attackers in normal attacks
        atk_map = {}
        # maps attackees to attackers in reverse attacks
        reverse_atk_map = {}

        # generate trivial deductions for all assumptions:
        for assumption in self.assumptions:
            deductions[assumption] = set()
            deductions[assumption].add(Deduction({assumption}, {assumption}))

        # generate supporting assumptions
        for sentence in generate_for:
            args = self.generate_arguments(sentence)
            if args:
                deductions[sentence] = set()

                for arg in args:
                    arg_deduction = Deduction(arg, {sentence})
                    deductions[sentence].add(arg_deduction)

                    if sentence.is_contrary and sentence.contrary() in self.assumptions:
                        trivial_arg = Deduction({sentence.contrary()}, {sentence.contrary()})

                        if self.attack_successful(arg, sentence.contrary()):
                            attacks.add(Attack(arg_deduction, trivial_arg, NORMAL_ATK))

                            f_arg = frozenset(arg)
                            if sentence.contrary() not in atk_map:
                                atk_map[sentence.contrary()] = set()
                            atk_map[sentence.contrary()].add(f_arg)

                        else:
                            attacks.add(Attack(trivial_arg, arg_deduction, REVERSE_ATK))

                            f_arg = frozenset(arg)
                            if f_arg not in reverse_atk_map:
                                reverse_atk_map[f_arg] = set()
                            reverse_atk_map[f_arg].add(sentence.contrary())

        all_deductions = ft.reduce(lambda x, y: x.union(y), deductions.values())

        for n_attackee, n_attacker_sets in atk_map.items():
            attackees = [ded for ded in all_deductions if n_attackee in ded.premise]
            for n_attacker in n_attacker_sets:
                attackers = [ded for ded in all_deductions if n_attacker.issubset(ded.premise)]
                for attackee in attackees:
                    for attacker in attackers:
                        attacks.add(Attack(attacker, attackee, NORMAL_ATK))

        for r_attackee, r_attacker_sets in reverse_atk_map.items():
            attackees = [ded for ded in all_deductions if r_attackee.issubset(ded.premise)]
            for r_attacker in r_attacker_sets:
                attackers = [ded for ded in all_deductions if r_attacker in ded.premise]
                for attackee in attackees:
                    for attacker in attackers:
                        attacks.add(Attack(attacker, attackee, REVERSE_ATK))

        return (deductions, attacks, all_deductions)

    def generate_arguments_and_attacks_for_contraries(self):
        """
        generate arguments supporting generate_for and all attacks between the arguments
        :return:
        """
        return self.generate_arguments_and_attacks([asm.contrary() for asm in self.assumptions])

    def attack_successful(self, attacker, attackee):
        """
        :param attacker: set of Sentences
        :param attackee: a Sentence
        :return: True if attacker attacks attackee successfully, false otherwise
        """
        for atk in attacker:
            if self.is_preferred(attackee, atk):
                return False
        return True

    def attacking_sentences_less_than_attackee(self, attacker, attackee):
        """
        :param attacker: set of Sentences
        :param attackee: a Sentence
        :return: the set of Sentences in attacker with lower preference than attackee
        """
        res = set()
        for atk in attacker:
            if self.is_preferred(attackee, atk):
                res.add(atk)

        return res

class Rule:
    def __init__(self, antecedent=set(), consequent=None):
        """
        :param antecedent: set of Sentences
        :param consequent: a Sentence
        """
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return self.antecedent == other.antecedent and \
               self.consequent == other.consequent

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (tuple(sort_sentences(list(self.antecedent))),
                self.consequent).__hash__()

class Sentence:
    def __init__(self, symbol=None, is_contrary=False):
        """
        :param symbol: string
        :param is_contrary: boolean
        """
        self.symbol = symbol
        self.is_contrary = is_contrary

    def __eq__(self, other):
        return self.is_contrary == other.is_contrary and \
               self.symbol == other.symbol

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (self.symbol, self.is_contrary).__hash__()

    def contrary(self):
        return Sentence(self.symbol, not self.is_contrary)

class Preference:
    def __init__(self, assump1=None, assump2=None, relation=NO_RELATION):
        """
        example: Preference(a,b,LESS_THAN) represents a < b
        :param assump1: first Sentence
        :param assump2: second Sentence
        :param relation: LESS_THAN, LESS_EQUAL or NO_RELATION
        """
        self.assump1 = assump1
        self.assump2 = assump2
        self.relation = relation

    def __eq__(self, other):
        return self.assump1 == other.assump1 and \
               self.assump2 == other.assump2 and \
               self.relation == other.relation

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (self.assump1, self.assump2, self.relation).__hash__()

class Attack:
    def __init__(self, attacker, attackee, type):
        """
        :param attacker: a Deudction whose conclusion is the contrary of the premise of the attackee
        :param attackee: a Deduction whose premise is the contrary of the conclusion of the attacker
        :param type: NORMAL_ATK or REVERSE_ATK
        """
        self.attacker = attacker
        self.attackee = attackee
        self.type = type

    def __eq__(self, other):
        return self.attacker == other.attacker and \
               self.attackee == other.attackee and \
               self.type == other.type

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (self.attacker, self.attackee, type).__hash__()

class Deduction:
    def __init__(self, premise, conclusion):
        """
        :param premise: set of Sentence
        :param conclusion: set of Sentence
        """
        self.premise = premise
        self.conclusion = conclusion

    def __eq__(self, other):
        return self.premise == other.premise and \
               self.conclusion == other.conclusion

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (tuple(sort_sentences(list(self.premise))),
                tuple(sort_sentences(list(self.conclusion)))).__hash__()

class CyclicPreferenceException(Exception):
    def __init__(self, message):
        self.message = message

class NonFlatException(Exception):
    def __init__(self, message):
        self.message = message

class InvalidPreferenceException(Exception):
    def __init__(self, message):
        self.message = message

class WCPViolationException(Exception):
    def __init__(self, message):
        self.message = message


def sort_sentences(list):
    """
    :param list: list of Sentences
    :return: list of Sentences sorted by symbol and is_contrary
    """
    return sorted(list, key=lambda sentence: (sentence.symbol, sentence.is_contrary))


def convert_to_attacks_between_sets(attacks):
    """
    :param attacks: collection for Attacks
    :return: set of tuples representing attacks, each with 3 elements:
             1: premise of the attacker (set of Sentences)
             2: premise of the attackee (set of Sentences)
             3. attack type
    """
    res = set()
    for atk in attacks:
        res.add((frozenset(atk.attacker.premise), frozenset(atk.attackee.premise), atk.type))
    return res

### USEFUL FOR DEBUGGING ###
def print_deduction(deduction):
    print(format_deduction)

def format_deduction(deduction):
    str = ""

    str += format_set(deduction.premise)
    str += " |- "
    str += format_set(deduction.conclusion)

    return str

def print_rule(rule):
    print("antecedent:")
    for ant in rule.antecedent:
        print(ant)
    print("consequent:")
    print(rule.consequent)

def print_attack(attack):
    str = ""

    if attack.type == NORMAL_ATK:
        str = "Normal Attack: "
    elif attack.type == REVERSE_ATK:
        str = "Reverse Attack: "

    str += format_deduction(attack.attacker)
    str += "   ->   "
    str += format_deduction(attack.attackee)

    print(str)

def format_sets(sets):
    str = ""

    it = iter(sets)
    first_set = next(it, None)
    if first_set is not None:
        str += format_set(first_set)
    for set in it:
        str += ", "
        str += format_set(set)

    return str

def format_set(set):
    str = "{"

    it = iter(set)
    first_sentence = next(it, None)
    if first_sentence is not None:
        str += format_sentence(first_sentence)
    for sentence in it:
        str += ", "
        str += format_sentence(sentence)

    str += "}"

    return str

def format_sentence(sentence):
    if sentence.is_contrary:
        return "!{}".format(sentence.symbol)
    else:
        return sentence.symbol





