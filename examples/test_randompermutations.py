from opbtest import OpbTestCase

#
# The randompermutations.psm4 Assembly file creates a random permutation of 4 numbers (0, 1, 2, 3)
# Scratchpad:
# 00 : 00 03 02 01 00 [...] -> original numbers, scrambled in unique permutation
# 10 : 00 02 02 01 00 [...] -> bitstream masks for these numbers: 0, 2, 2, 1
# 20 : 00 01 02 02 00 [...] -> scrambled in unique permutation
# 30 : [...]
# Out ports:
# 00: 00 06 0A 0C 02 [...]

class TestRandomPermutations(OpbTestCase):
    def setUp(self):
        pass
        #self.do_not_cleanup_files()

    def load_psm4_assertion(self):
        # mock out the PRNG call
        return self.load_file("randompermutations.psm4").replace("call random", "load seed, 3F").execute()

    def test_random_range_between_three_and_zero(self):
        # proc random_range(s0 is max, s2 is shifter, s3 is counter) {
        # we need to initialize these registers as "parameters". "return value" is in sA (seed)
        assert_that = self.load_file("randompermutations.psm4")\
            .replace("call random", "load seed, AF")\
            .setregs({"s0": 3})\
            .testproc("random_range")\
            .execute()

        assert_that.reg("sA").contains(2)

    def test_output_configuration_correct_in_output_ports(self):
        assert_that = self.load_psm4_assertion()
        assert_that.ports([1, 2, 3, 4, 5]).contains(["06", "0A", "0C", "02", "00"])

    def test_permutation_in_scratchpad(self):
        assert_that = self.load_psm4_assertion()
        assert_that.scratchpads(["0", "1", "2", "3"]).contains([0, 3, 2, 1])
        assert_that.scratchpads(["10", "11", "12", "13"]).contains([0, 2, 2, 1])
