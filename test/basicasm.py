

from opbtest import OpbTestCase

class TestBasicAsm(OpbTestCase):

    def test_basic_register_loading_form_file_psm4(self):
        result = self.execute_file("basic_register_loading.psm4")
        self.assertPsm(result).reg("s0").contains(1)

    def test_basic_register_loading_form_file_psm(self):
        result = self.execute_file("basic_register_loading.psm")
        self.assertPsm(result).reg("s0").contains(1)

    def test_basic_register_loading_inline(self):
        psm = """load s0, 1
output sD, FF"""

        result = self.execute_psm(psm)
        self.assertPsm(result).reg("s0").contains(1)
