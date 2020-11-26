import re

class JackTokenizer:
    def __init__(self, filename):
        f = open(filename, 'r')
        text = f.read()
        f.close()

        # remove comments //
        text = re.sub(r'\/\/.*', '', text)

        # remove comments /** */
        text = re.sub(r'\/\*(\*(?!\/)|[^*])*\*\/', '', text)

        self.keywords = ['class','constructor','function',
        'method','field','static','var','int',
        'char', 'boolean','void', 'true','false',
        'null', 'this', 'let', 'do', 'if','else',
        'while', 'return']

        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', 
        '-', '*', '/', '&', '|', '<', '>', '=', '~']

        self.regexIdentifier = r"[a-zA-Z_]+\w*"
        self.regexIntConst = r"[0-9]+"

        regex = r'\b' + self.regexIdentifier + r'\b|' + "|".join(self.keywords) + "|" + "|\\".join(self.symbols)+"|" + self.regexIntConst + "|\".*\""
        self.tokens = re.findall(regex, text)
        self.lengthTokens = len(self.tokens) 
        self.index = 0

    def rewind(self):
        self.index = 0

    def advance(self):
        self.index += 1

    def getToken(self):
        if(self.hasMoreTokens()):
            return self.tokens[self.index]

    def hasMoreTokens(self):
        return self.index < self.lengthTokens

    def tokenType(self):
        if self.getToken() in self.keywords:
            return "keyword"
        if self.getToken() in self.symbols:
            return "symbol"
        if self.getToken().isdigit():
            return "intConst"
        if re.match(self.regexIdentifier, self.getToken()):
            return "identifier"

        return "stringConst"