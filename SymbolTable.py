class SymbolTable:

    STATIC = 'static'
    FIELD = 'field'
    ARG = 'argument'
    VAR = 'local'

    def __init__(self):
        self.classLevel = {}
        self.subroutineLevel = {}
        self.countKinds = {
            self.STATIC: 0,
            self.FIELD: 0,
            self.ARG: 0,
            self.VAR: 0
        }

    def startSubroutine(self):
        self.subroutineLevel.clear()
        self.countKinds.update({
            self.ARG: 0,
            self.VAR: 0
        })

    def define(self, name, type, kind):

        item = {
            'name': name,
            'type': type,
            'kind': kind,
            'index': self.countKinds[kind]
        }

        if kind in [self.STATIC, self.FIELD]:
            self.classLevel.update({
                name : item
            })

        elif kind in [self.ARG, self.VAR]:
            self.subroutineLevel.update({
                name : item
            })

        self.countKinds[kind] += 1

    def varCount(self, kind):
        return self.countKinds[kind]

    def kindOf(self, name):
        return self.find(name, 'kind')

    def typeOf(self, name):
        return self.find(name, 'type')

    def indexOf(self, name):
        return self.find(name, 'index')
    
    def find(self, name, index):
        if name in self.subroutineLevel:
            return self.subroutineLevel[name].get(index)
        
        elif name in self.classLevel:
            return self.classLevel[name].get(index)

        raise RuntimeError("Variable {} not defined".format(name))
