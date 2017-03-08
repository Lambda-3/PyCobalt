import bz2


class TypeLookup(object):
    __separator = ' -----+++----- '

    def __init__(self, filename: str):
        self.__instance_types = {}

        with bz2.open(filename, 'rt') as f:
            for line in f:
                fields = line.split(self.__separator)
                self.__instance_types[fields[0].replace('<', '').replace('>', '')] = fields[1].replace('\n', '')

    def type(self, uri: str) -> str:
        return self.__instance_types[uri] if uri in self.__instance_types else ''
