import bz2


class TypeLookup(object):
    __separator = ' -----+++----- '

    def __init__(self, filename: str):
        self.__instanceTypes = {}

        with bz2.open(filename, 'rt') as f:
            for line in f:
                fields = line.split(self.__separator)
                self.__instanceTypes[fields[0].replace('<', '').replace('>', '')] = fields[1].replace('\n', '')

    def getType(self, uri: str) -> str:
        return self.__instanceTypes[uri] if uri in self.__instanceTypes else ''
