class OpbTestMockable():
    def __init__(self, case, filename):
        self.case = case
        self.filename = filename
        self.prepender = []
        self.inputs = {}
        self.proctotest = ""
        self.appender = ["\nopbtestquitfn: output sD, FF\n"]

    def testproc(self, procname):
        self.proctotest = procname
        return self
    def testfunc(self, funcname):
        return self.testproc(funcname)

    def setregs(self, regmap):
        for key, val in regmap.items():
            self.prepender.append("load " + key + ", " + str(val) + "\n")
        return self

    def mockinput(self, port, value):
        self.inputs[port] = value
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

            linenr = findlinebetween(data, self.proctotest + "(", "}")          # add (, could also have been a call
            data = data[0:linenr] + ["jump opbtestquitfn\n"] + data[linenr:]
            return data

        def setupinputs(data):
            newdata = []
            for line in data:
                if line.startswith("input "):
                    found = False
                    for key, value in self.inputs.items():
                        if ", " + str(key) in line or "," + str(key) in line:
                            newdata.append(line.split(",")[0].replace("input", "load") + ", " + str(value) + "\n")
                            found = True
                    if found is False:
                        newdata.append(line)
                else:
                    newdata.append(line)
            return newdata

        if len(self.proctotest) > 0:
            data = setupproc(data)
        if len(self.inputs) > 0:
            data = setupinputs(data)

        firstjump = findlinebetween(data, "jump", "jump")

        data = data[0:firstjump] + self.prepender + data[firstjump:] + self.appender
        with open(self.filename, 'w') as modified:
            modified.writelines(data)
        return self.case.execute_file(self.filename)