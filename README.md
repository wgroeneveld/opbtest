
## Open PicoBlaze Assembler Unit Test package

This python 3 package makes it easy for you to write PSM(4) Assembly - even **test-first**! 
Simply write a unit test for it in python, extending from `OpbTestCase`. It's easily integratable into your CI environment by leveraging the output of `python -m unittest`.

Example test case:

````python
from opbtest import OpbTestCase

class MyTestCase(OpbTestCase):
    def test_add_registers_counts_reg1_and_reg2_into_reg3(self):
        assert_that = self.load_file("functions.psm4")\
            .testproc("add_registers")\
            .setregs({"s0": 1, "s1": 2})\
            .execute()
        assert_that.reg("s5").contains(3)
````

Given the following Assembly:

```
jump main
proc add_registers(s0 is one, s1 is two, s5 is result) {
  load result, 0
  loop1:
    add result, 1
    sub one, 1
    jump NZ, loop1
  loop2:
    add result, 1
    sub two, 1
    jump NZ, loop2
}
main:
  ; this should not be executed
  load s5, 42
  load sD, FF
```

That's it! Load your Assembly file, apply setup (mocks, inputs), and verify expectations.

opbtest relies on [opbasm and opbsim](https://kevinpt.github.io/opbasm) to compile and evaluate your code. 
Both executables should be in your `$PATH`. 
The simulator will behave different compared to the actual hardware, so be aware that a set of green tests will not guarantee your code to work when deployed. 

### Installation

Use pip: `pip install opbtest`

Prerequirements: 

1. Python 3.x. Tested and written in Python 3.6
2. The command `opbsam` should be installed. (See above)
3. The command `opbsim` should be installed. (See above)


### API Documentation

Start by subclassing from `OpbTestCase` instead of unittest's usual `TestCase`
(you can still use all methods defined here, it's subclassed too.) Your IDE should recognize methods starting with `test_` as a unit test. 
For more information, consult the [Python 3 unittest framework documentation](https://docs.python.org/3/library/unittest.html).

#### Loading your Assembly

Base class: `OpbTestCase`

The following methods are possible to bootstrap your Assembly:

* use `load_file(filename)`. This does not evaluate yet, until you call `execute()`, which returns an `OpbTestAssertions` instance.
* use `execute_file(filename)`. This immediately evaluates by reading the file, returning an `OpbTestAssertions` instance.
* use `execute_psm(asmstring)`. This immediately evaluates the given string, returning an `OpbTestAssertions` instance.

For example, inline Assembly:

````python
    def test_basic_output_assertion(self):
        psm = """load s2, 5
                 output s2, 1
                 output sD, FF"""

        assert_that = self.execute_psm(psm)
        assert_that.port(1).contains(5)
        assert_that.ports(["1", "FF"]).contains([5, 0])
````

#### Assertions

Base class: `OpbTestAssertions`

The following can be asserted:

* `reg()`, `regs()`, `rega()`, `regsa()`, `regb()`, `regsb()`. Registers. `.reg("s0").contains(1)`. Max 2x16. No bank specified defaults to bank "a".
* `port()` and `ports()`. Output Ports. `.port(0).contains(1)`. Max 16x16
* `scratchpad()` and `scratchpads()`. Scratchpad. `.scratchpad(0).contains(1)` Max 4x16

Everything can be chained together, or be asserted in one line:

```python
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
``` 

Notice the difference: `scratchpads()` will accept an array, and `contains()` will accept the same length in values.
You can set the scratchpad/output port/... index as an `int` (0, 1, ...) or as a `str` in hex values ("0", "1F", "FF", ...)

**Assertion output**: if for instance the output ports do not match, the following message will appear in your test output window:

> AssertionError: Output dos not contain expected values: 
output ports_out 3 should contain 0 (hex: 00) but instead contains 12 (hex: 0C)

Since it's possible to assert hex values (as a `str`) or number values (as an `int`), the test output message always shows both. 

It is possible to write `assert_that.ports([1]).contains(["0A"])` and `assert_that.ports([1]).contains([10])`. Both assert the same thing and contain the same expectation values.

#### Testing only one procedure

If you don't want the whole thing to be executed, you can still use opbtest, and call `testproc(name)`:

````python
    def test_proc2_testproc_does_not_execute_rest_of_psm(self):
        assert_that = self.load_file("functions.psm4").testproc("proc2").execute()
        assert_that.regs(["s2", "s4"]).contains([0, 42])
````

given the following contents of functions.psm4:

```
use_stack(sF, 0x3F)

jump main

proc proc1(s0 is result := 1) {
    load result, 42
    call proc2
}

proc proc2(s4 is test) {
    load test, 42
}

main:
    load s2, 11
    add s2, 1

    output sD, FF
```

Only testing proc1, and nothing more, is usually tricky in Assembly because of the jump statement. opbtest will inject code into your Assembly to jump to the procedure to test, execute that, and jump to an exit label. That ensures no other state will be modified.

#### Mocking

If you explicitly do **not** want a certain procedure to be called, you can do so by calling `mockproc(procname)`. 
This will replace all `call procname` statements with dummy statements, hence never actually executing the procedure. 

You can replace your own statements with `replace(statement_to_replace, statement_to_replace_with)`. 

#### Injecting register values

Before calling `execute()`, you can preload register values using `setreg()`. 
For instance, `.setregs({"s5": 2, "s6": 3})` will preload register s5 with value 2 and register s6 with value 3. Psm statements like `output s5, 0` will load 2 into output port 0, because register s5 is preloaded.

#### Injecting input values

Before calling `execute()`, you can preload input port values using `mockinput()`.
For instance, `.mockinput(0, 4)` will preload input port 0 with value 4. Psm statements like `input s0, 0` will load 4 into register s4. 
opbtest acutally replaces the statement with `load s0, 4`, so no actual input statements will be processed.

### Debugging Tests

Somethings, a failing test does not clearly indicate the underlying problem. The Assembly source file is not the same source code as the code that is simulated to get to this result.
For example, when mocking, parts are replaced, and when registers are setup, extra loads are done. If you want to take a look at the Assembly file to be compiled and interpreted, add the following to your `setUp` testcase:

```python
    def setUp(self):
        self.do_not_cleanup_files()
```

This will leave the generated Assembly files in the test directory after test execution:

1. tmp_[timestamp].psm4
2. tmp_[timestamp].gen.psm - PicoBlaze macro expanded instructionset
3. tmp_[timestamp].fmt, .log metafiles
4. tmp_[timestamp].mem - binary.

Run the assembler yourself:

1. compiling: `opbasm --6 -c file.psm4` (or `--3` for PicoBlaze 3)
2. simulating: `opbsim -v -m:file.mem --pb6` (or `--pb3` for PicoBlaze 3)

For more information about the commandline flags, see the [Open PicoBlaze Assembler documentation](http://kevinpt.github.io/opbasm/).