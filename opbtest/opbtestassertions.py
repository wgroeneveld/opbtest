import functools


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

        if type(expected) is int or type(expected) is str:
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

