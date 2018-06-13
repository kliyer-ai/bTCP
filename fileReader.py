

class FileReader():

    def __init__(self):
        self.file = []

    def read(self, name):
        with open(name, 'rb', ) as file:
            self.file = file.read()

    def next(self, size):
        package = self.file[:size]
        self.file = self.file[size:]
        return package

    def empty(self):
        return len(self.file) == 0