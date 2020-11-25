from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from xml.sax.saxutils import escape
from os.path import splitext

class CompilationEngine:
    def __init__(self, filename):

        self.tokenizer = JackTokenizer(filename)
        self.types = ['int', 'char', 'boolean']
        self.operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        self.keywordsConstant = ['true', 'false', 'null', 'this']
        self.fileName = splitext(filename)[0]
        self.symbolTable = SymbolTable()
        self.vm = VMWriter(splitext(filename)[0])
        self.whileLabelNum = 0
        self.ifLabelNum = 0
    
    def compile(self):
        self.file = open(self.fileName + ".xml", "w")
        self.compileClass()
        self.file.close()
        self.vm.close()

    def compileClass(self):
        self.writeToXml("<class>")

        self.expect("class")
        self.className = self.tokenizer.getToken()
        self.expectType('identifier')
        self.expect("{")

        while self.tokenizer.getToken() in ['static', 'field']:
            self.compileClassVarDec()

        while self.tokenizer.getToken() in ['constructor', 'function', 'method']:
            self.compileSubroutine()

        self.expect("}")
        self.writeToXml("</class>")

    def compileClassVarDec(self):
        self.writeToXml('<classVarDec>')
        
        kind = self.tokenizer.getToken()
        self.expect(['field', 'static'])

        if self.tokenizer.getToken() in self.types or self.tokenizer.tokenType() == 'identifier':
            type = self.tokenizer.getToken()
            self.printToken()
            self.tokenizer.advance()

        name = self.tokenizer.getToken()
        self.expectType('identifier')

        self.symbolTable.define(name, type, kind)

        while self.tokenizer.getToken() == ",":
            self.expect(",")
            name = self.tokenizer.getToken()
            self.expectType('identifier')

            self.symbolTable.define(name, type, kind)

        self.expect(';')

        self.writeToXml('</classVarDec>')

    def compileSubroutine(self):
        self.writeToXml("<subroutineDec>")
        self.symbolTable.startSubroutine()
        self.whileLabelNum = 0
        self.ifLabelNum = 0

        subroutineType = self.tokenizer.getToken()
        self.expect(['constructor', 'function', 'method'])

        if self.tokenizer.getToken() in self.types + ['void'] or self.tokenizer.tokenType() == 'identifier':
            self.printToken()
            self.tokenizer.advance()

        functionName = self.className + '.' + self.tokenizer.getToken()

        self.expectType('identifier')
        self.expect("(")
        self.compileParameterList()
        self.expect(")")

        self.writeToXml("<subroutineBody>")
        self.expect("{")

        while self.tokenizer.getToken() == 'var':
            self.compileVarDec()

        self.vm.writeFunction(functionName, self.symbolTable.varCount(SymbolTable.VAR))
        if subroutineType == 'constructor':
            self.vm.writePush(VMWriter.CONST, self.symbolTable.varCount(SymbolTable.FIELD))
            self.vm.writeCall("Memory.alloc", 1)
            self.vm.writePop(VMWriter.POINTER, 0)
        elif subroutineType == 'method':
            self.vm.writePush(VMWriter.ARG, 0)
            self.vm.writePop(VMWriter.POINTER, 0)

        self.compileStatements()
        self.expect("}")
        self.writeToXml("</subroutineBody>")

        self.writeToXml("</subroutineDec>")

    def compileParameterList(self):
        self.writeToXml("<parameterList>")

        if self.tokenizer.getToken() in self.types or self.tokenizer.tokenType() == 'identifier':
            type = self.tokenizer.getToken()
            
            self.printToken() 
            self.tokenizer.advance()

            name = self.tokenizer.getToken()
            self.symbolTable.define(name, type, SymbolTable.ARG)

            self.expectType('identifier')

        while self.tokenizer.getToken() == ',':
            self.expect(",")
            if self.tokenizer.getToken() not in self.types and self.tokenizer.tokenType() != 'identifier':
                self.errorExpected(self.tokenizer.getToken(), '|'.join(self.types + ['identifier']))

            type = self.tokenizer.getToken()

            self.printToken()
            self.tokenizer.advance()

            name = self.tokenizer.getToken()
            self.symbolTable.define(name, type, SymbolTable.ARG)

            self.expectType('identifier')

        self.writeToXml("</parameterList>")

    def compileVarDec(self):
        self.writeToXml("<varDec>")

        self.expect('var')

        if self.tokenizer.getToken() in self.types or self.tokenizer.tokenType() == 'identifier':
            type = self.tokenizer.getToken()

            self.printToken()
            self.tokenizer.advance()
        
        self.symbolTable.define(self.tokenizer.getToken(),type, self.symbolTable.VAR)
        self.expectType('identifier')

        while self.tokenizer.getToken() == ",":
            self.expect(",")
            self.symbolTable.define(self.tokenizer.getToken(), type, self.symbolTable.VAR)
            self.expectType('identifier')

        self.expect(';')

        self.writeToXml("</varDec>")

    def compileStatements(self):
        self.writeToXml("<statements>")

        statatements = ['while', 'if', 'let', 'return', 'do']

        while self.tokenizer.getToken() in statatements:
            token = self.tokenizer.getToken()
            if token == 'while':
                self.compileWhile()
            elif token == 'if':
                self.compileIf()
            elif token == 'let':
                self.compileLet()
            elif token == 'do':
                self.compileDo()
            elif token == 'return':
                self.compileReturn()

        self.writeToXml("</statements>")

    def compileDo(self):
        self.writeToXml('<doStatement>')

        self.expect("do")
        identifier = self.tokenizer.getToken()
        self.expectType("identifier")

        self.compileSubroutineCall(identifier)

        self.expect(";")
        self.vm.writePop(VMWriter.TEMP, 0)

        self.writeToXml('</doStatement>')

    def compileExpressionList(self):
        self.writeToXml('<expressionList>')

        count = 0
        if self.tokenizer.getToken() != ")":
            self.compileExpression()
            count += 1
            while self.tokenizer.getToken() == ",":
                self.expect(",")
                self.compileExpression()
                count += 1

        self.writeToXml('</expressionList>')

        return count
        
    def compileIf(self):
        self.writeToXml('<ifStatement>')

        labelElse = "IF_ELSE{}".format(self.ifLabelNum) 
        labelEnd = "IF_END{}".format(self.ifLabelNum)
        self.ifLabelNum += 1

        self.expect("if")
        self.expect("(")
        self.compileExpression()
        
        self.vm.writeArithmetic(VMWriter.NOT)
        self.vm.writeIf(labelElse)

        self.expect(")")
        self.expect("{")

        self.compileStatements()
        self.vm.writeGoto(labelEnd)

        self.expect("}")

        self.vm.writeLabel(labelElse)

        if self.tokenizer.getToken() == "else":
            self.expect('else')
            self.expect("{")
            self.compileStatements()
            self.expect("}")

        self.vm.writeLabel(labelEnd)

        self.writeToXml('</ifStatement>')

    def compileWhile(self):
        self.writeToXml('<whileStatement>')

        labelExp = "WHILE_EXP{}".format(self.whileLabelNum)
        labelEnd = "WHILE_END{}".format(self.whileLabelNum)
        self.whileLabelNum += 1

        self.vm.writeLabel(labelExp)
        self.expect("while")
        self.expect("(")

        self.compileExpression()
        self.vm.writeArithmetic(VMWriter.NOT)
        self.vm.writeIf(labelEnd)

        self.expect(")")
        self.expect("{")
        self.compileStatements()
        self.vm.writeGoto(labelExp)
        self.expect("}")

        self.vm.writeLabel(labelEnd)

        self.writeToXml('</whileStatement>')

    def compileReturn(self):
        self.writeToXml('<returnStatement>')

        self.expect("return")
        if self.tokenizer.getToken() != ";":
            self.compileExpression()
            self.vm.writeReturn()
        else:
            self.vm.writePush(VMWriter.CONST, 0)
            self.vm.writeReturn()

        self.expect(";")

        self.writeToXml("</returnStatement>")

    def compileLet(self):
        self.writeToXml('<letStatement>')

        self.expect("let")

        ident = self.tokenizer.getToken()

        self.expectType('identifier')

        isArray = False
        if self.tokenizer.getToken() == "[":
            self.expect("[")
            self.compileExpression()

            self.vm.writePush(self.resolveSegment(ident), self.symbolTable.indexOf(ident))
            self.vm.writeArithmetic(VMWriter.ADD)

            self.expect("]")
            isArray = True

        self.expect("=")
        self.compileExpression()

        if isArray:
            self.vm.writePop(VMWriter.TEMP, 0)
            self.vm.writePop(VMWriter.POINTER, 1)
            self.vm.writePush(VMWriter.TEMP, 0)
            self.vm.writePop(VMWriter.THAT, 0)
        else:
            self.vm.writePop(self.resolveSegment(ident), self.symbolTable.indexOf(ident))

        self.expect(";")

        self.writeToXml('</letStatement>')

    def compileExpression(self):
        self.writeToXml('<expression>')

        self.compileTerm()

        while self.tokenizer.getToken() in self.operators:
            operator = self.tokenizer.getToken()

            self.expect(self.operators)
            self.compileTerm()

            self.compileOperator(operator)
        
        self.writeToXml('</expression>')

    def compileOperator(self, operator):
        if operator is '+':
            self.vm.writeArithmetic(self.vm.ADD)
        
        elif operator is '-':
            self.vm.writeArithmetic(self.vm.SUB)

        elif operator is '*':
            self.vm.writeCall("Math.multiply", 2)

        elif operator is '/':
            self.vm.writeCall("Math.divide", 2)
        elif operator is '&':
            self.vm.writeArithmetic(self.vm.AND)
        elif operator is '|':
            self.vm.writeArithmetic(self.vm.OR)
        elif operator is '~':
            self.vm.writeArithmetic(self.vm.NOT)
        elif operator is '>':
            self.vm.writeArithmetic(self.vm.GT)
        elif operator is '<':
            self.vm.writeArithmetic(self.vm.LT)
        elif operator is '=':
            self.vm.writeArithmetic(self.vm.EQ)



    def compileTerm(self):
        self.writeToXml("<term>")

        if self.tokenizer.tokenType() == 'keyword':
            if self.tokenizer.getToken() == 'true':
                self.vm.writePush(VMWriter.CONST, 0)
                self.vm.writeArithmetic(VMWriter.NOT)

            elif self.tokenizer.getToken() in ['false', 'null']:
                self.vm.writePush(VMWriter.CONST, 0)

            elif self.tokenizer.getToken() == 'this':
                self.vm.writePush(VMWriter.POINTER, 0)                        

            self.expect(self.keywordsConstant)

        elif self.tokenizer.tokenType() == 'identifier':

            identifier = self.tokenizer.getToken()
            self.expectType('identifier')

            if self.tokenizer.getToken() == '[':
                self.expect('[')
                self.compileExpression()

                self.vm.writePush(self.resolveSegment(identifier), self.symbolTable.indexOf(identifier))
                self.vm.writeArithmetic(VMWriter.ADD)

                self.expect(']')
                self.vm.writePop(VMWriter.POINTER, 1)
                self.vm.writePush(VMWriter.THAT, 0)

            elif self.tokenizer.getToken() in ['.', '(']:
                self.compileSubroutineCall(identifier)
            else:
                segment = self.symbolTable.kindOf(identifier)
                if segment == 'field':
                    segment = 'this'
                
                self.vm.writePush(segment, self.symbolTable.indexOf(identifier))

        elif self.tokenizer.tokenType() == 'intConst':
            self.vm.writePush(self.vm.CONST, self.tokenizer.getToken())
            self.expectType('intConst')

        elif self.tokenizer.tokenType() == 'stringConst':
            string = self.tokenizer.getToken()
            self.expectType('stringConst')

            self.vm.writePush(VMWriter.CONST, len(string))
            self.vm.writeCall('String.new', 1)

            for i in string:
                self.vm.writePush(VMWriter.CONST, ord(i))
                self.vm.writeCall('String.appendChar', 2)
            
        elif self.tokenizer.getToken() == '~':
            self.expect('~')
            self.compileTerm()
            self.vm.writeArithmetic(VMWriter.NOT)

        elif self.tokenizer.getToken() == '-':
            self.expect('-')
            self.compileTerm()
            self.vm.writeArithmetic(VMWriter.NEG)
        elif self.tokenizer.getToken() == '(':
            self.expect('(')
            self.compileExpression()
            self.expect(')')

        self.writeToXml("</term>")

    def compileSubroutineCall(self, identifier):
        if self.tokenizer.getToken() == '(':
            self.vm.writePush(VMWriter.POINTER, 0)

            self.expect('(')
            nArgs = self.compileExpressionList()
            nArgs += 1
            self.expect(')')
                
            functionName = self.className + '.' + identifier
            self.vm.writeCall(functionName, nArgs)
        else:
            if self.tokenizer.getToken() == ".":
                self.expect(".")

                if self.symbolTable.hasOf(identifier):
                    self.vm.writePush(self.resolveSegment(identifier), self.symbolTable.indexOf(identifier))
                    nameFunction = self.symbolTable.typeOf(identifier) + '.' + self.tokenizer.getToken()
                else:
                    nameFunction = identifier + '.' + self.tokenizer.getToken()
        
                self.expectType("identifier")
                self.expect("(")
                nArgs = self.compileExpressionList()
                nArgs += 1
            else:
                nameFunction = self.className + '.' + identifier
                self.expect("(")
                nArgs = self.compileExpressionList()
                nArgs += 1
            

            self.expect(")")
            self.vm.writeCall(nameFunction, nArgs)

    def resolveSegment(self, ident):
        segment = self.symbolTable.kindOf(ident)
        if segment == 'field':
            segment = VMWriter.THIS

        return segment

    def expect(self, expected):
        if type(expected) == list:
            if self.tokenizer.getToken() not in expected: 
                self.errorExpected(self.tokenizer.getToken(), "|".join(expected))
        else:
            if self.tokenizer.getToken() != expected:
                self.errorExpected(self.tokenizer.getToken(), expected)

        self.printToken()
        self.tokenizer.advance()

    def expectType(self, expected):
        if type(expected) == list:
            if self.tokenizer.tokenType() not in expected: 
                self.errorExpected(self.tokenizer.getToken(), "|".join(expected))
        else:
            if self.tokenizer.tokenType() != expected:
                self.errorExpected(self.tokenizer.getToken(), expected)
            
        self.printToken()
        self.tokenizer.advance()
    
    def printToken(self):
        tokenType = self.tokenizer.tokenType()

        self.writeToXml("<" + tokenType + ">" + escape(self.tokenizer.getToken()) + "</" + tokenType + ">")

    def errorExpected(self, atual, expected):
        exit("Expected " + expected + ", " + atual + " given")
    
    def writeToXml(self, el):
        self.file.write(el)