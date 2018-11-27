
from unittest import TestCase
import subprocess, os, time, json, glob

class OpbTestAssertions():
    def __init__(self, json, case):
        self.jsondata = json
        self.case = case
        self.register = None

    def reg(self, register):
        if not register.startswith("s"):
            self.case.fail("Register name should start with 's', followed with 0-F")

        self.register = int(register[1], 16)
        return self

    def contains(self, expected):
        if self.register is None:
            self.case.fail("First call reg() to assert which register to check!")

        self.case.assertReg(self.jsondata, "a", self.register, expected)

class OpbTestCase(TestCase):

    def tearDown(self):
        for file in glob.glob('tmp_*'):
            os.remove(file)
        for file in glob.glob('*.gen.psm'):
            os.remove(file)
        for file in glob.glob('*.log'):
            os.remove(file)
        for file in glob.glob('*.mem'):
            os.remove(file)
        for file in glob.glob('*.fmt'):
            os.remove(file)

    def execute_file(self, filename):
        psm4 = "psm4" in filename
        r = subprocess.call("opbasm -{} -c {}".format("6" if psm4 else "3", filename), shell=True)
        self.assertTrue(r == 0, "Opbasm compilation failed of source; filename: " + filename)

        try:
            json_out = subprocess.check_output("opbsim -v -j -m:{} --{}".format(filename.replace(".psm4" if psm4 else ".psm", ".mem"), "pb6" if psm4 else "pb3"), shell=True)
        except subprocess.CalledProcessError as e:
            self.fail("Opbsim simulation failed with: " + '\n>>> '.join(('\n' + str(e.output)).splitlines()).lstrip())

        json_out = json.loads(json_out)
        self.assertTrue(json_out['termination'] == 'termNormal', 'Simulation failed with ' + json_out['termination'])
        return json_out

    def execute_psm(self, psm):
        with open("tmp_" + str(time.time()) + ".psm4", "w") as file:
            file.write(psm)
        return self.execute_file(file.name)

    def assertPsm(self, jsondata):
        return OpbTestAssertions(jsondata, self)

    def assertReg(self, jsondata, bank, nr, expected):
        self.assertEqual(expected, jsondata["regs_" + bank][nr])
