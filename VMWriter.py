class VMWriter:
    ADD = 'add'
    SUB = 'sub'
    NEG = 'neg'
    NOT = 'not'
    AND = "and"
    OR = "or"
    LT = "lt"
    GT = "gt"
    EQ = "eq"

    STATIC = 'static'
    CONST = 'constant'
    POINTER = 'pointer'
    THIS = 'this'
    ARG = 'argument'
    TEMP = 'temp'
    THAT = 'that'

    def __init__(self, fileName):
        self.file = open(fileName + ".vm", "w")

    def writePush(self, segment, index):
        self.file.write("push {} {}\n".format(segment, index))

    def writePop(self, segment, index):
        self.file.write("pop {} {}\n".format(segment, index))

    def writeArithmetic(self, command):
        self.file.write("{}\n".format(command))

    def writeCall(self, name, nArgs):
        self.file.write("call {} {}\n".format(name, nArgs))
    
    def writeFunction(self, name, nLocals):
        self.file.write("function {} {}\n".format(name, nLocals))

    def writeReturn(self):
        self.file.write("return\n")

    def writeLabel(self, label):
        self.file.write("label {}\n".format(label))

    def writeIf(self, label):
          self.file.write("if-goto {}\n".format(label))

    def writeGoto(self, label):
        self.file.write("goto {}\n".format(label))

    def close(self):
        self.file.close()


# vm = VMWriter('Teste')

# vm.writePush('const', 0)
# vm.writePush('const', 1)
# vm.writeArithmetic('add')
# vm.writePop('this', 0)