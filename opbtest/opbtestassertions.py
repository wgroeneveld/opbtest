import functools


class OpbTestBaseAssertions():
    def __init__(self, json, case):
        self.jsondata = json
        self.case = case

    def dong(self):
        print("dong")

    def _tocontain(self, expected):
        raise Exception("to implement in sublcass")

    def _contains(self, expected):
        raise Exception("to implement in sublcass")

    def _getlist_to_fill(self):
        raise Exception("to implement in sublcass")

    def contains(self, expected):
        listtofill = self._getlist_to_fill()
        if listtofill is None:
            self.case.fail("First setup what to check by calling other methods!")

        if type(expected) is int or type(expected) is str:
            return self._tocontain(expected)

        if type(expected) is not list:
            self.case.fail("Expected array as expected values!")
        if len(expected) != len(listtofill):
            self.case.fail("Given values and expected results arrays length does not match!")
        self.fail_if_results(self._contains(expected))

    def fail_if_results(self, results):
        if len(results) > 0:
            self.case.fail(
                "Output dos not contain expected values: \n" + functools.reduce(lambda a, b: a + "\n" + b, results))


class OpbTestRegAssertions(OpbTestBaseAssertions):
    def __init__(self, json, case, bank):
        super().__init__(json, case)
        self.registers = None
        self.bank = bank

    def torawregistername(self, register):
        return int(register[1], 16)

    def assertregistername(self, register):
        if not register.startswith("s"):
            self.case.fail("Register name should start with 's', followed with 0-F")

    def reg(self, register):
        self.assertregistername(register)
        self.registers = [int(register[1], 16)]
        return self

    def regs(self, registers):
        if type(registers) is not list:
            self.case.fail("Expected a list of registers")
        self.registers = list(map(lambda reg: self.torawregistername(reg), registers))
        return self

    def _getlist_to_fill(self):
        return self.registers

    def _tocontain(self, expected):
        for register in self.registers:
            result = self.case.checkReg(self.jsondata, self.bank, register, expected)
            if result != "":
                self.case.fail(result)

    def _contains(self, expected):
        results = []
        for i in range(0, len(expected)):
            result = self.case.checkReg(self.jsondata, self.bank, self.registers[i], expected[i])
            if result != "":
                results.append(result)
        return results


class OpbTestIndexAssertions(OpbTestBaseAssertions):
    def __init__(self, json, case, maxindex, json_index_name):
        super().__init__(json, case)
        self.indices = None
        self.maxindex = maxindex
        self.json_index_name = json_index_name

    def assertindexname(self, index):
        if index < 0 or index > self.maxindex:
            self.case.fail("Index should be between 0 and 255, but instead was " + index)

    def torawindex(self, index):
        if type(index) is str:
            index = int(index, 16)
        self.assertindexname(index)
        return index

    def _index(self, index):
        self.indices = [self.torawindex(index)]
        return self

    def _indices(self, indices):
        if type(indices) is not list:
            self.case.fail("Expected a list of indices")
        self.indices = list(map(lambda port: self.torawindex(port), indices))
        return self

    def _getlist_to_fill(self):
        return self.indices

    def _tocontain(self, expected):
        for index in self.indices:
            result = self.case._check(self.json_index_name, self.jsondata, index, expected)
            if result != "":
                self.case.fail(result)

    def _contains(self, expected):
        results = []
        for i in range(0, len(expected)):
            result = self.case._check(self.json_index_name, self.jsondata, self.indices[i], expected[i])
            if result != "":
                results.append(result)
        return results


class OpbTestOutputAssertions(OpbTestIndexAssertions):
    def __init__(self, json, case):
        super().__init__(json, case, 16 * 16, "ports_out")

    def port(self, port):
        return self._index(port)

    def ports(self, ports):
        return self._indices(ports)


class OpbTestScratchAssertions(OpbTestIndexAssertions):
    def __init__(self, json, case):
        super().__init__(json, case, 16 * 4, "scratchpad")

    def scratchpad(self, port):
        return self._index(port)

    def scratchpads(self, ports):
        return self._indices(ports)


class OpbTestAssertions():
    def __init__(self, json, case):
        self.jsondata = json
        self.case = case

    def port(self, port):
        return OpbTestOutputAssertions(self.jsondata, self.case).port(port)

    def ports(self, port):
        return OpbTestOutputAssertions(self.jsondata, self.case).ports(port)

    def scratchpad(self, index):
        return OpbTestScratchAssertions(self.jsondata, self.case).scratchpad(index)

    def scratchpads(self, indices):
        return OpbTestScratchAssertions(self.jsondata, self.case).scratchpads(indices)

    def regs(self, registers):
        return OpbTestRegAssertions(self.jsondata, self.case, "a").regs(registers)

    def reg(self, register):
        return OpbTestRegAssertions(self.jsondata, self.case, "a").reg(register)

    def regsa(self, registers):
        return OpbTestRegAssertions(self.jsondata, self.case, "a").regs(registers)

    def rega(self, register):
        return OpbTestRegAssertions(self.jsondata, self.case, "a").reg(register)

    def regsb(self, registers):
        return OpbTestRegAssertions(self.jsondata, self.case, "b").regs(registers)

    def regb(self, register):
        return OpbTestRegAssertions(self.jsondata, self.case, "b").reg(register)
