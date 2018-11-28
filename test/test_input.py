from opbtest import OpbTestCase


class TestInput(OpbTestCase):

    def setUp(self):
        pass
        #self.do_not_cleanup_files()

    def test_setup_input(self):
        assert_that = self.load_file("input.psm4").mockinput(0, 4).execute()
        assert_that.regs(["s0", "s1"]).contains(4)