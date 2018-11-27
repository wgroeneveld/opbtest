

from opbtest import OpbTestCase

class TestBasicAsm(OpbTestCase):

    def test_basic_register_loading(self):
        psm = """load s0, 1
output sD, FF"""

        result = self.execute_psm(psm)

        self.assertPsm(result).reg("s0").contains(1)
