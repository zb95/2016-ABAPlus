import numpy as np

LESS_THAN = 1
LESS_EQUAL = 2
NO_RELATION = 3

CANNOT_BE_DERIVED = -1

NORMAL_ATK = 1
REVERSE_ATK = 2

class ABA_Plus:
    def __init__(self, assumptions=set(), preferences=set(), rules=set()):
        self.assumptions = assumptions
        self.preferences = preferences
        self.rules = rules

        self.calc_transitive_closure()

    # returns Flase if error with preferences, e.g. a < a, True otherwise
    def calc_transitive_closure(self):
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
                if i == j and relation == LESS_THAN:
                    return False
                if i != j and relation != NO_RELATION:
                    assump1 = assump_list[i]
                    assump2 = assump_list[j]
                    self.preferences.add(Preference(assump1, assump2, relation))

        return True

    # in relation_matrix, use 1 for < and 2 for <=
    def _transitive_closure(self, relation_matrix):
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

    def __str__(self):
        return str(self.__dict__)

    def attacking_rules(self, sentence):
        return self.deriving_rules(sentence.contrary())

    def deriving_rules(self, sentence):
        der_rules = set()
        for rule in self.rules:
            if rule.consequent == sentence:
                der_rules.add(rule)
        return der_rules

    def get_relation(self, assump1, assump2):
        for pref in self.preferences:
            if pref.assump1 == assump1 and pref.assump2 == assump2:
                return pref.relation
        return NO_RELATION

    def is_preferred(self, assump1, assump2):
        return self.get_relation(assump2, assump1) == LESS_THAN

    def WCP_fulfilled(self, contradictor, assumption, antecedent):
        negated_contr = contradictor.contrary()
        deduce_from = antecedent.copy()
        deduce_from.add(assumption)
        deduce_from.remove(contradictor)
        return self.deduction_exists(negated_contr, deduce_from)

    def deduction_exists(self, to_deduce, deduce_from):
        rules_applied = set()
        deduced = deduce_from.copy()
        while True:
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
            if not new_rule_used:
                break
        return False

    def direct_decution_exists(self, to_deduce, deduce_from):
        for rule in self.rules:
            if rule.consequent == to_deduce and rule.antecedent.issubset(deduce_from):
                return True
        return False

    def set_combinations(self, iterable):
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
        violation_found = False
        for assump in self.assumptions:
            att_rules = self.attacking_rules(assump)
            for rule in att_rules:
                for contradictor in rule.antecedent:
                    result = self.preference_check(assump, contradictor, rule.antecedent, set())
                    if result == False:
                        violation_found = True
                    elif result == CANNOT_BE_DERIVED:
                        return True
        return not violation_found

    def preference_check(self, assumption, contradictor, antecedent, sentences_seen):
        if contradictor in self.assumptions and \
           self.is_preferred(assumption, contradictor) and \
           not self.WCP_fulfilled(contradictor, assumption, antecedent):
            return False
        elif contradictor not in self.assumptions:
            der_rules = self.deriving_rules(contradictor)
            if not der_rules:
                return CANNOT_BE_DERIVED
            sentences_seen.add(contradictor)
            for rule in der_rules:
                violation_found = False
                for ant in rule.antecedent:
                    if ant not in sentences_seen:
                        result =  self.preference_check(assumption, ant, rule.antecedent, sentences_seen.copy())
                        if result == False:
                            violation_found = True
                        elif result == CANNOT_BE_DERIVED:
                            violation_found = False
                            break
                if violation_found == True:
                    return False
        return True

    #TODO: rename to avoid confusion between supporting sets and 'arguments' in abstract argumentation
    def generate_arguments(self, generate_for):
        return self._generate_arguments(generate_for, set())

    def _generate_arguments(self, generate_for, sentences_seen):
        if generate_for in self.assumptions:
            return {frozenset({generate_for})}

        sentences_seen.add(generate_for)
        der_rules = self.deriving_rules(generate_for)
        results = set()
        for rule in der_rules:
            supporting_assumptions = set()
            args_lacking = False
            if not rule.antecedent:
                empty_set = set()
                empty_set.add(frozenset())
                supporting_assumptions.add(frozenset(empty_set))
            for ant in rule.antecedent:
                if ant not in sentences_seen:
                    args = self._generate_arguments(ant, sentences_seen.copy())
                    if not args:
                        args_lacking = True
                        break
                    supporting_assumptions.add(frozenset(args))

            if not args_lacking:
                results = results.union(self.set_combinations(supporting_assumptions))
        return results

    def generate_arguments_and_attacks(self, generate_for):
        deductions = {}
        attacks = set()

        # generate trivial deductions for all assumptions:
        for assumption in self.assumptions:
            deductions[assumption] = set()
            deductions[assumption].add(Deduction({assumption}, {assumption}))
            #print(next(iter(deductions[assumption])))

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
                        else:
                            attacks.add(Attack(trivial_arg, arg_deduction, REVERSE_ATK))

        # generate attacks between supporting sets
        for _, deduction_set in deductions.items():
            for deduction in deduction_set:
                for sentence in deduction.premise:
                    if sentence.contrary() in deductions:
                        attacking_args = deductions[sentence.contrary()]
                        for attacking_arg in attacking_args:
                            if self.attack_successful(attacking_arg.premise, sentence):
                                attacks.add(Attack(attacking_arg, deduction, NORMAL_ATK))
                            else:
                                attacks.add(Attack(deduction, attacking_arg, REVERSE_ATK))

        return (deductions, attacks)



    def attack_successful(self, attacker, attackee):
        for atk in attacker:
            if self.get_relation(atk, attackee) == LESS_THAN:
                return False
        return True

    def generate_attack(self, deduction):
        for p in deduction.premise:
            pass


class Rule:
    def __init__(self, antecedent=set(), consequent=None):
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return self.antecedent == other.antecedent and \
               self.consequent == other.consequent

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (tuple(self.antecedent), self.consequent).__hash__()

class Sentence:
    def __init__(self, symbol=None, is_contrary=False):
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
        self.premise = premise
        self.conclusion = conclusion

    def __eq__(self, other):
        return self.premise == other.premise and \
               self.conclusion == other.conclusion

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (tuple(self.premise), tuple(self.conclusion)).__hash__()





