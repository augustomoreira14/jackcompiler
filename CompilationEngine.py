from JackTokenizer import JackTokenizer
from xml.sax.saxutils import escape
from os.path import splitext

class CompilationEngine:
    def __init__(self, filename):

        self.tokenizer = JackTokenizer(filename)
        self.types = ['int', 'char', 'boolean']
        self.operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        self.keywordsConstant = ['true', 'false', 'null', 'this']
        self.fileName = splitext(filename)[0]
    
    def compile(self):
        self.file = open(self.fileName + ".xml", "w")
        self.compileClass()
        self.file.close()

    def compileClass(self):
        self.writeToXml("<class>")

        self.expect("class")
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

        self.expect(['field', 'static'])

        if self.tokenizer.getToken() in self.types or self.tokenizer.tokenType() == 'identifier':
            self.printToken()
            self.tokenizer.advance()

        self.expectType('identifier')

        while self.tokenizer.getToken() == ",":
            self.expect(",")
            self.expectType('identifier')

        self.expect(';')

        self.writeToXml('</classVarDec>')

    def compileSubroutine(self):
        self.writeToXml("<subroutineDec>")
        
        self.expect(['construct', 'function', 'method'])
        self.expect(self.types + ['void'])
        self.expectType('identifier')
        self.expect("(")
        self.compileParameterList()
        self.expect(")")

        self.writeToXml("<subroutineBody>")
        self.expect("{")

        while self.tokenizer.getToken() == 'var':
            self.compileVarDec()

        self.compileStatements()
        self.expect("}")
        self.writeToXml("</subroutineBody>")

        self.writeToXml("</subroutineDec>")

    def compileParameterList(self):
        self.writeToXml("<parameterList>")

        if self.tokenizer.getToken() in self.types or self.tokenizer.tokenType() == 'identifier':
            self.printToken()
            self.tokenizer.advance()
            self.expectType('identifier')

        while self.tokenizer.getToken() == ',':
            self.expect(",")
            if self.tokenizer.getToken() not in self.types and self.tokenizer.tokenType() != 'identifier':
                self.errorExpected(self.tokenizer.getToken(), '|'.join(self.types + ['identifier']))

            self.printToken()
            self.tokenizer.advance()
            self.expectType('identifier')

        self.writeToXml("</parameterList>")

    def compileVarDec(self):
        self.writeToXml("<varDec>")

        self.expect('var')

        if self.tokenizer.getToken() in self.types or self.tokenizer.tokenType() == 'identifier':
            self.printToken()
            self.tokenizer.advance()

        self.expectType('identifier')

        while self.tokenizer.getToken() == ",":
            self.expect(",")
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
        self.expectType("identifier")

        if self.tokenizer.getToken() == ".":
            self.expect(".")
            self.expectType("identifier")

        self.expect("(")
        self.compileExpressionList()
        self.expect(")")
        self.expect(";")

        self.writeToXml('</doStatement>')

    def compileExpressionList(self):
        self.writeToXml('<expressionList>')
        if self.tokenizer.getToken() != ")":
            self.compileExpression()
            while self.tokenizer.getToken() == ",":
                self.expect(",")
                self.compileExpression()

        self.writeToXml('</expressionList>')
        
    def compileIf(self):
        self.writeToXml('<ifStatement>')

        self.expect("if")
        self.expect("(")
        self.compileExpression()
        self.expect(")")
        self.expect("{")
        self.compileStatements()
        self.expect("}")

        if self.tokenizer.getToken() == "else":
            self.expect('else')
            self.expect("{")
            self.compileStatements()
            self.expect("}")

        self.writeToXml('</ifStatement>')

    def compileWhile(self):
        self.writeToXml('<whileStatement>')

        self.expect("while")
        self.expect("(")
        self.compileExpression()
        self.expect(")")
        self.expect("{")
        self.compileStatements()
        self.expect("}")

        self.writeToXml('</whileStatement>')

    def compileReturn(self):
        self.writeToXml('<returnStatement>')

        self.expect("return")
        if self.tokenizer.getToken() != ";":
            self.compileExpression()

        self.expect(";")

        self.writeToXml("</returnStatement>")

    def compileLet(self):
        self.writeToXml('<letStatement>')

        self.expect("let")
        self.expectType('identifier')

        if self.tokenizer.getToken() == "[":
            self.expect("[")
            self.compileExpression()
            self.expect("]")

        self.expect("=")
        self.compileExpression()
        self.expect(";")

        self.writeToXml('</letStatement>')

    def compileExpression(self):
        self.writeToXml('<expression>')

        self.compileTerm()

        while self.tokenizer.getToken() in self.operators:
            self.expect(self.operators)
            self.compileTerm()
        
        self.writeToXml('</expression>')

    def compileTerm(self):
        self.writeToXml("<term>")
        
        if self.tokenizer.tokenType() == 'keyword':
            self.expect(self.keywordsConstant)
        else:
            self.expectType(['identifier', 'intConst', 'stringConst'])

        self.writeToXml("</term>")
    
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