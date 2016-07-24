from aba_plus import *
import re

ASSUMP_PREDICATE = "myAsm"
CONTR_PREDICATE = "contrary"
RULE_PREDICATE = "myRule"
# myPrefLT(a, b) represents a < b
LT_PREDICATE = "myPrefLT"
# myPrefLE(a, b) represents a <= b
LE_PREDICATE = "myPrefLE"

ASSUMP_REGEX = r"myAsm\((.+)\)"
CONTR_REGEX = r"contrary\((.+),(.+)\)"
RULE_REGEX = r"myRule\((.+),\[(.*)\]\)"
LT_REGEX = r"myPrefLT\((.+),(.+)\)"
LE_REGEX = r"myPrefLE\((.+),(.+)\)"

def generate_aba_plus_framework_from_file(filename):
    file = open(filename, 'r')
    input = file.read().replace("\n", "")
    file.close()
    return generate_aba_plus_framework(input)

def generate_aba_plus_framework(input_string):
    declarations = input_string.split(".")

    assump_declarations = [decl for decl in declarations if ASSUMP_PREDICATE in decl]
    assumptions = generate_assumptions(assump_declarations)

    contr_declarations = [decl for decl in declarations if CONTR_PREDICATE in decl]
    contr_map = generate_contraries_map(contr_declarations)

    rule_declarations = [decl for decl in declarations if RULE_PREDICATE in decl]
    rules = generate_rules(rule_declarations, contr_map)

    pref_declarations = [decl for decl in declarations if (LT_PREDICATE in decl) or (LE_PREDICATE in decl)]
    preferences = generate_preferences(pref_declarations)

    return ABA_Plus(assumptions, preferences, rules)

def generate_assumptions(assump_decls):
    assumptions = set()

    for decl in assump_decls:
        # remove spaces
        cleaned_decl = decl.replace(" ", "")
        match = re.match(ASSUMP_REGEX, cleaned_decl)
        if match:
            symbol = match.group(1)
            assumptions.add(Sentence(symbol, False))

    return assumptions

# can only assumptions have contraries?
def generate_contraries_map(contr_decls):
    #maps symbols to contraries
    map = {}

    for decl in contr_decls:
        cleaned_decl = decl.replace(" ", "")
        match = re.match(CONTR_REGEX, cleaned_decl)
        if match:
            sentence = match.group(1)
            contrary = match.group(2)
            map[contrary] = Sentence(sentence, True)

    return map

def generate_rules(rule_decls, map):
    rules = set()

    for decl in rule_decls:
        cleaned_decl = decl.replace(" ", "")
        match = re.match(RULE_REGEX, cleaned_decl)
        if match:
            consequent_symbol = match.group(1)
            consequent = translate_symbol(consequent_symbol, map)

            antecedent = set()
            if match.group(2) != "":
                antecedent_symbols = match.group(2).split(",")

                for ant in antecedent_symbols:
                    antecedent.add(translate_symbol(ant, map))

            rules.add(Rule(antecedent, consequent))

    return rules

# TODO: check if sentences are assumptions
def generate_preferences(pref_decls):
    preferences = set()

    for decl in pref_decls:
        cleaned_decl = decl.replace(" ", "")

        relation = NO_RELATION
        match = re.match(LT_REGEX, cleaned_decl)
        if match:
            relation = LESS_THAN
        else:
            match = re.match(LE_REGEX, cleaned_decl)
            if match:
                relation = LESS_EQUAL
        if relation != NO_RELATION:
            sentence_symbol1 = match.group(1)
            sentence1 = Sentence(sentence_symbol1, False)
            sentence_symbol2 = match.group(2)
            sentence2 = Sentence(sentence_symbol2, False)
            preferences.add(Preference(sentence1, sentence2, relation))

    return preferences

def translate_symbol(symbol, map):
    if symbol in map:
        return map[symbol]
    else:
        return Sentence(symbol, False)