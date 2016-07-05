import numpy as np

LESS_THAN = 1
LESS_EQUAL = 2
NO_RELATION = 3

class ABA_Plus:
    def __init__(self, assumptions=set(), preferences=set(), rules=set()):
        self.assumptions = assumptions
        self.preferences = preferences
        self.rules = rules

    def __str__(self):
        return str(self.__dict__)

    def attacking_rules(self, assumption):
        return self.deriving_rules(assumption.contrary())

    def deriving_rules(self, assumption):
        der_rules = set()
        for rule in self.rules:
            if rule.consequent == assumption:
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

    def check_WCP(self):
        for assump in self.assumptions:
            att_rules = self.attacking_rules(assump)
            for rule in att_rules:
                for contradictor in rule.antecedent:
                    if not self.preference_check(assump, contradictor, rule.antecedent):
                        return False
        return True

    def preference_check(self, assumption, contradictor, antecedent):
        if self.is_preferred(assumption, contradictor) and \
           not self.WCP_fulfilled(contradictor, assumption, antecedent):
            return False
        elif contradictor not in self.assumptions:
            der_rules = self.deriving_rules(contradictor)
            for rule in der_rules:
                for ant in rule.antecedent:
                    if not self.preference_check(assumption, ant, rule.antecedent):
                        return False
        return True


class Rule:
    def __init__(self, antecedent=None, consequent=None):
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return self.antecedent == other.antecedent and \
               self.consequent == other.consequent

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (tuple(self.antecedent), self.consequent).__hash__()

class Predicate:
    def __init__(self, symbol=None, is_negated=False):
        self.symbol = symbol
        self.is_negated = is_negated

    def __eq__(self, other):
        return self.is_negated == other.is_negated and \
               self.symbol == other.symbol

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (self.symbol, self.is_negated).__hash__()

    def contrary(self):
        return Predicate(self.symbol, not self.is_negated)

class Preference:
    def __init__(self, assump1=None, assump2=None, relation=NO_RELATION):
        self.assump1 = assump1
        self.assump2 = assump2
        self.relation = relation

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return (self.assump1, self.assump2, self.relation).__hash__()

# in relation_matrix, use 1 for < and 2 for <=
def transitive_closure(relation_matrix):
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
