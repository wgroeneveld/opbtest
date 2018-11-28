from unittest import TestCase
import subprocess, os, time, json, glob, functools


class OpbTestAssertions():
    def __init__(self, json, case):
        self.jsondata = json
        self.case = case
        self.registers = None

    def regs(self, registers):
        if type(registers) is not list:
            self.case.fail("Expected a list of registers")
        self.registers = list(map(lambda reg: self.torawregistername(reg), registers))
        return self

    def torawregistername(self, register):
        return int(register[1], 16)

    def assertregistername(self, register):
        if not register.startswith("s"):
            self.case.fail("Register name should start with 's', followed with 0-F")

    def reg(self, register):
        self.assertregistername(register)
        self.registers = [int(register[1], 16)]
        return self

    def tocontain(self, expected):
        for register in self.registers:
            result = self.case.checkReg(self.jsondata, "a", register, expected)
            if result != "":
                self.case.fail(result)

    def contains(self, expected):
        if self.registers is None:
            self.case.fail("First call reg()/regs() to assert which register to check!")

        if type(expected) is int:
            return self.tocontain(expected)

        if type(expected) is not list:
            self.case.fail("Expected array as expected register values!")
        if len(expected) != len(self.registers):
            self.case.fail("Given registers and expected results arrays do not match!")

        results = []
        for i in range(0, len(expected)):
            result = self.case.checkReg(self.jsondata, "a", self.registers[i], expected[i])
            if result != "":
                results.append(result)
        if len(results) > 0:
            self.case.fail(
                "Registers do not contain expected values: \n" + functools.reduce(lambda a, b: a + "\n" + b, results))


class OpbTestMockable():
    def __init__(self, case, filename):
        self.case = case
        self.filename = filename
        self.prepender = []
        self.proctotest = ""
        self.appender = ["\nopbtestquitfn: output sD, FF\n"]

    def testproc(self, procname):
        self.proctotest = procname
        return self

    def setregs(self, regmap):
        for key, val in regmap.items():
            self.prepender.append("load " + key + ", " + str(val) + "\n")
        return self

    def execute(self):
        with open(self.filename, 'r') as original:
            data = original.readlines()

        def findlinebetween(data, statement1, statement2):
            linenr = 0
            startcounting = False
            for line in data:
                if statement1 in line:
                    startcounting = True
                if startcounting and statement2 in line:
                    break
                linenr += 1

            if linenr + 1 == len(data):
                self.case.fail("No statements between " + statement1 + " and " + statement2 + " found")
            return linenr

        def setupproc(data):
            self.prepender.append("jump " + self.proctotest + "\n")

            linenr = findlinebetween(data, "proc " + self.proctotest, "}")
            data = data[0:linenr] + ["jump opbtestquitfn\n"] + data[linenr:]
            return data

        if len(self.proctotest) > 0:
            data = setupproc(data)

        firstjump = findlinebetween(data, "jump", "jump")

        data = data[0:firstjump] + self.prepender + data[firstjump:] + self.appender
        with open(self.filename, 'w') as modified:
            modified.writelines(data)
        return self.case.execute_file(self.filename)


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
        return json_out

    def execute_psm(self, psm):
        with open("tmp_" + str(time.time()) + ".psm4", "w") as file:
            file.write(psm)
        return self.execute_file(file.name)

    def assertPsm(self, jsondata):
        return OpbTestAssertions(jsondata, self)

    def checkReg(self, jsondata, bank, nr, expected):
        actual = jsondata["regs_" + bank][nr]
        if int(str(expected), 16) == actual:
            return ""
        return "reg " + bank + "," + str(nr) + " should contain " + str(expected) + " but instead contains " + str(
            actual)
