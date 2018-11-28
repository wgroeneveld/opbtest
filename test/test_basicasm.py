

from opbtest import OpbTestCase

class TestBasicAsm(OpbTestCase):

    def setUp(self):
        pass
        #self.do_not_cleanup_files()

    def test_basic_register_loading_form_file_psm4(self):
        self.execute_file("basic_register_loading.psm4").reg("s0").contains(1)

    def test_basic_register_loading_form_file_psm(self):
        self.execute_file("basic_register_loading.psm").reg("s0").contains(1)

    def test_basic_scratchpad_assertion(self):
        psm = """load s0, 1
                 store s0, (s0)
                 load s0, 2
                 store s0, (s0)
                 load s0, 3
                 store s0, (s0)
                 output sD, FF"""

        assert_that = self.execute_psm(psm)
        assert_that.scratchpad(1).contains(1)
        assert_that.scratchpads(["0", "1", "2", "3"]).contains([0, 1, 2, 3])

    def test_basic_output_assertion(self):
        psm = """load s2, 5
                 output s2, 1
                 output sD, FF"""

        assert_that = self.execute_psm(psm)
        assert_that.port(1).contains(5)
        assert_that.ports(["1", "FF"]).contains([5, 0])

    def test_basic_register_loading_inline(self):
        psm = """load s0, 1
                 output sD, FF"""

        self.execute_psm(psm).reg("s0").contains(1)
