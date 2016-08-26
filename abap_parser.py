from aba_plus_ import *
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

DUPLICATE_USE_FOUND = "_duplicate"

def generate_aba_plus_framework_from_file(filename):
    file = open(filename, 'r')
    input = file.read()
    file.close()
    return generate_aba_plus_framework(input)

def generate_aba_plus_framework(input_string):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(input_string)
    print(input_string.count("\r"))
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    input = input_string.replace('\r', '')
    input = input.replace('\n', '')
    #input = input_string.split("\n")
    #input = ''.join(input)
    print(input)
    declarations = input.split(".")


    assump_declarations = [decl for decl in declarations if ASSUMP_PREDICATE in decl]
    assumptions = generate_assumptions(assump_declarations)

    contr_declarations = [decl for decl in declarations if CONTR_PREDICATE in decl]
    res = generate_contraries_map(contr_declarations)
    contr_map = res[0]
    aux_rules = res[1]

    rule_declarations = [decl for decl in declarations if RULE_PREDICATE in decl]
    rules = generate_rules(rule_declarations, contr_map, aux_rules)

    pref_declarations = [decl for decl in declarations if (LT_PREDICATE in decl) or (LE_PREDICATE in decl)]
    preferences = generate_preferences(pref_declarations)

    return (ABA_Plus(assumptions, preferences, rules), contr_map)

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

'''
def generate_contraries_map(contr_decls):
    #maps symbols to contraries
    map = {}
    duplicate_symbols = set()
    aux_rules = set()

    for decl in contr_decls:
        cleaned_decl = decl.replace(" ", "")
        match = re.match(CONTR_REGEX, cleaned_decl)
        if match:
            sentence = match.group(1)
            contrary = match.group(2)

            if (contrary in map) and (map[contrary] != DUPLICATE_USE_FOUND):
                print("1")
                duplicate_symbols.add(sentence)
                duplicate_symbols.add(contrary)
                existing_sentence = map[contrary]
                duplicate_symbols.add(existing_sentence)
                map[contrary] = DUPLICATE_USE_FOUND
                aux_rules.add(Rule({Sentence(contrary, False)},
                              Sentence(existing_sentence, True)))

            if sentence in map.values():
                print("2")
                existing_contrary = list(map)[list(map.values()).index(sentence)]
                if map[existing_contrary] != DUPLICATE_USE_FOUND:
                    duplicate_symbols.add(sentence)
                    duplicate_symbols.add(contrary)
                    map[existing_contrary] = DUPLICATE_USE_FOUND
                    duplicate_symbols.add(existing_contrary)
                    aux_rules.add(Rule({Sentence(existing_contrary, False)},
                                  Sentence(sentence, True)))

            #if ((contrary in map) and (map[contrary] == DUPLICATE_USE_FOUND)) \
            #        or (sentence in duplicate_sentences):
            if (sentence in duplicate_symbols) or (contrary in duplicate_symbols):
                print("3")
                map[contrary] = DUPLICATE_USE_FOUND
                duplicate_symbols.add(contrary)
                duplicate_symbols.add(sentence)
                aux_rules.add(Rule({Sentence(contrary, False)},
                              Sentence(sentence, True)))
            else:
                print("4")
                map[contrary] = sentence

    return (map, aux_rules)
'''

# TODO: check that only assumptions have contraries
# TODO: throw exception when multiple contraries for the same assumption detected and vice versa
def generate_contraries_map(contr_decls):
    # maps symbols to contraries
    map = {}

    for decl in contr_decls:
        cleaned_decl = decl.replace(" ", "")
        match = re.match(CONTR_REGEX, cleaned_decl)
        if match:
            sentence = match.group(1)
            contrary = match.group(2)
            map[contrary] = sentence

    return (map, set())

def generate_rules(rule_decls, map, aux_rules):
    rules = aux_rules

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
    if (symbol in map) and (map[symbol] != DUPLICATE_USE_FOUND):
        return Sentence(map[symbol], True)
    else:
        return Sentence(symbol, False)