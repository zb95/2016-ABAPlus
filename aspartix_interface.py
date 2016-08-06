from aba_plus_ import *
import subprocess
import re

from sys import platform as _platform
if _platform == "win32":
    DLV_IDEAL_COMMAND = "dlv {} {} -filter=ideal -n=1"
else:
    DLV_IDEAL_COMMAND = "./dlv {} {} -filter=ideal -n=1"

CLINGO = "clingo"
DLV = "dlv"

CLINGO_COMMAND = "clingo {} {} 0"


CLINGO_ANSWER = "Answer:"
DLV_ANSWER = "Best model:"

CLINGO_REGEX = r"in\((\d+)\)"
DLV_IDEAL_REGEX = r"ideal\((\d+)\)"

ADMISSIBLE_FILE = "adm.dl"
STABLE_FILE= "stable.dl"
IDEAL_FILE = "ideal.dl"
COMPLETE_FILE = "comp.dl"
PREFERRED_FILE = "prefex_gringo.lp"
GROUNDED_FILE = "ground.dl"



class ASPARTIX_Interface:
    def __init__(self, aba_plus):
        self.aba_plus = aba_plus

    '''
    def generate_input_file_for_clingo(self, filename):
        res = self.aba_plus.generate_arguments_and_attacks_for_contraries()
        deductions = res[0]
        self.attacks = res[1]
        #for atk in self.attacks:
         #   print_attack(atk)
          #  print()
        ''''''
        for _, v in deductions.items():
            for d in v:
                print_deduction(d)
                print()
        ''''''
        #maps arguments to indices, which are used to represent the arguments in the input file
        self.arguments = []
        for _, deduction_set in deductions.items():
            for deduction in deduction_set:
                self.arguments.append(deduction)

        for i in range(0,len(self.arguments)):
            print(i)
            print_deduction(self.arguments[i])
        f = open(filename, 'w')

        for idx in range(0, len(self.arguments)):
            f.write("arg({}).\n".format(idx))

        for atk in self.attacks:
            idx_attacker = self.arguments.index(atk.attacker)
            idx_attackee = self.arguments.index(atk.attackee)
            f.write("att({}, {}).\n".format(idx_attacker, idx_attackee))

        f.close()
        '''



    def generate_input_file_for_clingo(self, filename):
        res = self.aba_plus.generate_arguments_and_attacks_for_contraries()
        deductions = res[2]
        attacks = res[1]
        #for atk in self.attacks:
         #   print_attack(atk)
          #  print()
        '''
        for _, v in deductions.items():
            for d in v:
                print_deduction(d)
                print()
        '''
        #maps arguments to indices, which are used to represent the arguments in the input file
        self.arguments = []
        for deduction in deductions:
            if deduction.premise not in self.arguments:
                self.arguments.append(deduction.premise)

        self.attacks = set()
        for atk in attacks:
            self.attacks.add((frozenset(atk.attacker.premise),
                              frozenset(atk.attackee.premise)))

        for i in range(0,len(self.arguments)):
            print(i)
            print(format_set(self.arguments[i]))

        f = open(filename, 'w')

        for idx in range(0, len(self.arguments)):
            f.write("arg({}).\n".format(idx))

        for atk in self.attacks:
            idx_attacker = self.arguments.index(atk[0])
            idx_attackee = self.arguments.index(atk[1])
            f.write("att({}, {}).\n".format(idx_attacker, idx_attackee))

        f.close()

    def calculate_admissible_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO_COMMAND, input_filename, ADMISSIBLE_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_stable_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO_COMMAND, input_filename, STABLE_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_ideal_extensions(self, input_filename):
        return self.calculate_extensions(DLV_IDEAL_COMMAND, input_filename, IDEAL_FILE, DLV_ANSWER, DLV_IDEAL_REGEX)

    def calculate_complete_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO_COMMAND, input_filename, COMPLETE_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_preferred_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO_COMMAND, input_filename, PREFERRED_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_grounded_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO_COMMAND, input_filename, GROUNDED_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_extensions(self, command, input_filename, encoding_filename, answer_header, regex):
        '''res = subprocess.run(command.format(input_filename, encoding_filename),
                             stdout=subprocess.PIPE,
                             universal_newlines=True)

        #print(res.stdout)
        if answer_header not in res.stdout:
            return set()


        results = res.stdout.split(answer_header)

        '''
        res = subprocess.Popen(command.format(input_filename, encoding_filename).split(" "),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = res.stdout.read().decode("utf-8")

        print(output)

        if answer_header not in output:
            return set()

        results = output.split(answer_header)

        extension_sets = set()
        answer_sets = results[1:len(results)+1]
        for answer in answer_sets:
           # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            #print(answer)
            matches = re.findall(regex, answer)
            extension = set()
            for m in matches:
                #print(m)
                arg = self.arguments[int(m)]
                #print(s)
                extension = extension.union(arg)
                #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                #print(extension)
            #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            #print(frozenset(extension))
            extension_sets.add(frozenset(extension))

        return extension_sets

    def calculate_admissible_arguments_extensions(self, input_filename):
        return self.calculate_arguments_extensions(CLINGO_COMMAND, input_filename, ADMISSIBLE_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_stable_arguments_extensions(self, input_filename):
        return self.calculate_arguments_extensions(CLINGO_COMMAND, input_filename, STABLE_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_ideal_arguments_extensions(self, input_filename):
        return self.calculate_arguments_extensions(DLV_IDEAL_COMMAND, input_filename, IDEAL_FILE, DLV_ANSWER, DLV_IDEAL_REGEX)

    def calculate_complete_arguments_extensions(self, input_filename):
        return self.calculate_arguments_extensions(CLINGO_COMMAND, input_filename, COMPLETE_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_preferred_arguments_extensions(self, input_filename):
        return self.calculate_arguments_extensions(CLINGO_COMMAND, input_filename, PREFERRED_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_grounded_arguments_extensions(self, input_filename):
        return self.calculate_arguments_extensions(CLINGO_COMMAND, input_filename, GROUNDED_FILE, CLINGO_ANSWER, CLINGO_REGEX)

    def calculate_arguments_extensions(self, command, input_filename, encoding_filename, answer_header, regex):
        res = subprocess.Popen(command.format(input_filename, encoding_filename).split(" "),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = res.stdout.read().decode("utf-8")

        if answer_header not in output:
            return set()

        results = output.split(answer_header)

        # maps sets of sentences to sets of conclusions
        extension_dict = {}
        answer_sets = results[1:len(results)+1]
        for answer in answer_sets:
            matches = re.findall(regex, answer)
            extension = set()
            conclusions = set()
            for m in matches:
                arg = self.arguments[int(m)]
                extension = extension.union(arg)
            conclusions = self.aba_plus.generate_all_deductions(extension)
            extension = frozenset(extension)
            if extension in extension_dict:
                extension_dict[extension] =  extension_dict[extension].union(conclusions)
            else:
                extension_dict[extension] = conclusions

        return extension_dict


