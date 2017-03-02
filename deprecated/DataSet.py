__author__ = 'heroico'

import gzip

#
class DataSet(object):
    """A list of values for a thing we care about"""
    def __init__(self,name=None,index=None, data = []):
        self.data = data
        self.name = name
        self.index = index


class DataSetFileUtilities(object):
    @classmethod
    def loadFromFile(cls, data_file_name = None, header_name=None):
        data_set = None
        with open(data_file_name, 'rb') as file:
            data_set = cls._loadDataSetFromFile(file, header_name)
            data_set.name = data_file_name
        return data_set

    @classmethod
    def loadFromCompressedFile(cls, data_file_name = None, header_name=None):
        data_set = None
        with gzip.open(data_file_name, 'rb') as file:
            data_set = cls._loadDataSetFromFile(file, header_name)
            data_set.name = data_file_name
        return data_set

    @classmethod
    def _loadDataSetFromFile(cls,file, header_name):
        read_first_line = False
        data = []
        for i,line in enumerate(file):
            if i == 0 and header_name is not None:
                assert line.strip("\n") == header_name
                continue
            data.append(line.strip("\n"))
        data_set = DataSet()
        data_set.data = data
        return data_set

#
class DataSetCollection(object):
    """A list of values for a thing we care about"""
    def __init__(self):
        self.sets = []

