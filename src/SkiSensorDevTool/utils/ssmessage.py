class SSMessage:

    commandSize = 8
    dummyChar = '\x7E'

    def __init__(self, name, params = {}, description = None, callback = None):
        self.name = self.buildCommand(name)
        self.description = description
        self.callback = callback
        self.params = params

    def buildCommand(self, name):
        encodedName = (name.encode('utf-8'))

        if len(encodedName) < SSMessage.commandSize:
            for i in range(SSMessage.commandSize - len(encodedName)):
                encodedName += self.dummyChar.encode('utf-8')
                #print(encodedName)

        return encodedName