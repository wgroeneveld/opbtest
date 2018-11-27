
from unittest import TestCase
import subprocess, os, time, json, glob

class OpbTestAssertions():
    def __init__(self, json, case):
        self.jsondata = json
        self.case = case
        self.register = None

    def reg(self, register):
        self.register = register
        return self

    def contains(self, expected):
        if self.register is None:
            self.case.fail("First call reg() to assert which register to check!")

        self.case.assertReg(self.jsondata, "a", int(self.register[1], 16), expected)

class OpbTestCase(TestCase):

    def tearDown(self):
        for file in glob.glob('tmp_*'):
            pass
            os.remove(file)

    def execute_psm(self, psm):
        with open("tmp_" + str(time.time()) + ".psm4", "w") as file:
            file.write(psm)

        r = subprocess.call("opbasm -6 -c " + file.name, shell=True)
        self.assertTrue(r == 0, "Opbasm compilation failed of source: " + psm)

        try:
            json_out = subprocess.check_output("opbsim -v -j -m:" + file.name.replace(".psm4", ".mem"), shell=True)
        except subprocess.CalledProcessError as e:
            self.fail("Opbsim simulation failed with: " + '\n>>> '.join(('\n' + str(e.output)).splitlines()).lstrip())

        json_out = json.loads(json_out)
        self.assertTrue(json_out['termination'] == 'termNormal', 'Simulation failed with ' + json_out['termination'])
        return json_out

    def assertPsm(self, jsondata):
        return OpbTestAssertions(jsondata, self)

    def assertReg(self, jsondata, bank, nr, expected):
        self.assertEqual(expected, jsondata["regs_" + bank][nr])
