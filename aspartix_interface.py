from aba_plus import *

class ASPARTIX_Interface:
    def __init__(self, aba_plus):
        self.aba_plus = aba_plus

    def generate_input_file_for_clingo(self, filename):
        res = self.aba_plus.generate_arguments_and_attacks_for_contraries()
        deductions = res[0]
        self.attacks = res[1]

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

