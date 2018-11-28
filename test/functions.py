
from opbtest import OpbTestCase

class TestFunctions(OpbTestCase):

    def setUp(self):
        pass
        #self.do_not_cleanup_files()

    def test_unknownproc_should_fail(self):
        try:
            self.load_file("functions.psm4").testproc("wazza").execute()
            self.fail("Expected assertion error to occur")
        except AssertionError:
            pass

    def test_setregs_unknownregs_should_fail(self):
        try:
            self.load_file("functions.psm4").setregs({"wazza": 11}).execute()
            self.fail("Expected assertion error to occur")
        except AssertionError:
            pass

    def test_proc3_adds_to_existing_register(self):
        result = self.load_file("functions.psm4").testproc("proc3").setregs({"s5": 2}).execute()
        self.assertPsm(result).reg("s5").contains(3)

    def test_proc2_testproc_does_not_execute_rest_of_psm(self):
        result = self.load_file("functions.psm4").testproc("proc2").execute()
        self.assertPsm(result).regs(["s2", "s4"]).contains([0, 42])

    def test_proc1_calls_proc2(self):
        result = self.load_file("functions.psm4").testproc("proc1").execute()
        self.assertPsm(result).regs(["s0", "s4"]).contains([42, 42])

    def test_func1_calls_func1(self):
        result = self.load_file("functions.psm4").testfunc("func1").execute()
        self.assertPsm(result).reg("s1").contains(52)
