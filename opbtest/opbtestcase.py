import glob
import json
import os
import subprocess
import time
from unittest import TestCase

from opbtest.opbtestassertions import OpbTestAssertions
from opbtest.opbtestmockable import OpbTestMockable


class OpbTestCase(TestCase):

    def do_not_cleanup_files(self):
        self.nocleanup = True

    def do_cleanup_files(self):
        self.nocleanup = False

    @classmethod
    def setUpClass(cls):
        """On inherited classes, run our `setUp` method"""
        # Inspired via http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class/17696807#17696807
        if cls is not OpbTestCase and cls.setUp is not OpbTestCase.setUp:
            orig_setUp = cls.setUp
            def setUpOverride(self, *args, **kwargs):
                OpbTestCase.setUp(self)
                return orig_setUp(self, *args, **kwargs)
            cls.setUp = setUpOverride

    def setUp(self):
        self.do_cleanup_files()

    def tearDown(self):
        if self.nocleanup:
            return

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

    def assertfile_exists(self, filename):
        self.assertTrue(os.path.exists(filename), "Filename " + filename + " does not exist!")

    def load_file(self, filename):
        self.assertfile_exists(filename)

        tmpname = "tmp_" + str(time.time()) + ".psm4"
        with open(tmpname, "w") as file:
            with open(filename, "r") as input:
                lines = input.readlines()
            file.writelines(lines)

        return OpbTestMockable(self, tmpname)

    def execute_file(self, filename):
        self.assertfile_exists(filename)
        psm4 = "psm4" in filename
        r = subprocess.call("opbasm -{} -c {}".format("6" if psm4 else "3", filename), shell=True)
        self.assertTrue(r == 0, "Opbasm compilation failed of source; filename: " + filename)

        try:
            json_out = subprocess.check_output(
                "opbsim -v -j -m:{} --{}".format(filename.replace(".psm4" if psm4 else ".psm", ".mem"),
                                                 "pb6" if psm4 else "pb3"), shell=True)
        except subprocess.CalledProcessError as e:
            self.fail("Opbsim simulation failed with: " + '\n>>> '.join(('\n' + str(e.output)).splitlines()).lstrip())

        json_out = json.loads(json_out)
        self.assertTrue(json_out['termination'] == 'termNormal', 'Simulation failed with ' + json_out['termination'])
        return self.assertPsm(json_out)

    def execute_psm(self, psm):
        with open("tmp_" + str(time.time()) + ".psm4", "w") as file:
            file.write(psm)
        return self.execute_file(file.name)

    def assertPsm(self, jsondata):
        return OpbTestAssertions(jsondata, self)

    def _print_expectation(self, expected):
        return str(expected) + " (hex: " + hex(expected).replace("0x", "").upper().zfill(2) + ")"

    def _check(self, jsonindex, jsondata, index, expected):
        actual = jsondata[jsonindex][index]
        # try to convert both to the same type. acutal will always be an int (hex valued)
        if type(expected) is str:
            expected = int(expected, 16)

        if expected == actual:
            return ""
        return "output " + jsonindex + " " + str(index) + " should contain " + self._print_expectation(expected) + " but instead contains " + self._print_expectation(actual)

    def checkPort(self, jsondata, port, expected):
        self._check("ports_out", jsondata, port, expected)

    def checkReg(self, jsondata, bank, nr, expected):
        actual = jsondata["regs_" + bank][nr]
        if type(expected) is int:
            expected = int(str(expected), 16)
        if expected == actual:
            return ""
        return "reg " + bank + "," + self._print_expectation(nr) + " should contain " + str(expected) + " but instead contains " + str(actual)
