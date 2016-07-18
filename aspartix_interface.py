from aba_plus import *
import subprocess
import re

CLINGO = "clingo"
DLV = "dlv"

CLINGO_COMMAND = "{} {} {} 0"
DLV_COMMAND = "{} {} {} -filter=in"

ADMISSIBLE_FILE = "adm.dl"
STABLE_FILE= "stable.dl"
IDEAL_FILE = "ideal.dl"
COMPLETE_FILE = "comp.dl"
PREFERRED_FILE = "prefex_gringo.lp"
GROUNDED_FILE = "ground.dl"

class ASPARTIX_Interface:
    def __init__(self, aba_plus):
        self.aba_plus = aba_plus

    def generate_input_file_for_clingo(self, filename):
        res = self.aba_plus.generate_arguments_and_attacks_for_contraries()
        deductions = res[0]
        self.attacks = res[1]
        '''
        for _, v in deductions.items():
            for d in v:
                print_deduction(d)
                print()
        '''
        #maps arguments to indices, which are used to represent the arguments in the input file
        self.arguments = []
        for _, deduction_set in deductions.items():
            for deduction in deduction_set:
                self.arguments.append(deduction)

        f = open(filename, 'w')

        for idx in range(0, len(self.arguments)):
            f.write("arg({}).\n".format(idx))

        for atk in self.attacks:
            idx_attacker = self.arguments.index(atk.attacker)
            idx_attackee = self.arguments.index(atk.attackee)
            f.write("att({}, {}).\n".format(idx_attacker, idx_attackee))

        f.close()

    def calculate_admissible_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO, input_filename, ADMISSIBLE_FILE)

    def calculate_stable_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO, input_filename, STABLE_FILE)

    def calculate_ideal_extensions(self, input_filename):
        return self.calculate_extensions(DLV, input_filename, IDEAL_FILE)

    def calculate_complete_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO, input_filename, COMPLETE_FILE)

    def calculate_preferred_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO, input_filename, PREFERRED_FILE)

    def calculate_grounded_extensions(self, input_filename):
        return self.calculate_extensions(CLINGO, input_filename, GROUNDED_FILE)

    def calculate_extensions(self, solver, input_filename, extension_filename):
        COMMAND = ""

        if solver == CLINGO:
            COMMAND = CLINGO_COMMAND
        elif solver == DLV:
            COMMAND = DLV_COMMAND

        res = subprocess.run(COMMAND.format(solver, input_filename, extension_filename),
                             stdout=subprocess.PIPE,
                             universal_newlines=True)

        matches = re.findall(r"in\((\d+)\)", res.stdout)
        extensions = set()
        for m in matches:
            s = self.arguments[int(m)].premise
            extensions.add(frozenset(s))

        return extensions


