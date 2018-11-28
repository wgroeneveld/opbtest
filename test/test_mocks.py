from opbtest import OpbTestCase


class TestMocks(OpbTestCase):

    def test_mockproc_replaces_call_statements_with_dummies(self):
        assert_that = self.load_file("mocks.psm4").mockproc("myproc").execute()
        assert_that.reg("s0").contains(0)

    def test_replace_replaces_statement_with_given(self):
        assert_that = self.load_file("mocks.psm4").replace("load s0, 11", "load s0, 3").execute()
        assert_that.reg("s0").contains(3)

    def test_do_not_replace_anything(self):
        assert_that = self.load_file("mocks.psm4").execute()
        assert_that.reg("s0").contains(11)
