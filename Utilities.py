__author__ = 'heroico'

import os
import gzip
import csv

def hapName(name):
    return name + ".hap.gz"

def legendName(name):
    return name + ".legend.gz"

def dosageName(name):
    return name + ".dosage.gz"

def dosageTextName(name):
    return name + ".dosage.txt.gz"

def dosageNamesFromFolder(folder):
    names = namesWithPatternFromFolder(folder, ".dosage.gz")
    return names

def hapNamesFromFolder(folder):
    names = namesWithPatternFromFolder(folder, ".hap.gz")
    return names

def legendNamesFromFolder(folder):
    names = namesWithPatternFromFolder(folder, ".legend.gz")
    return names

def namesWithPatternFromFolder(folder, pattern):
    contents = os.listdir(folder)
    names = []
    for content in contents:
        if pattern in content:
            name = content.split(pattern)[0]
            names.append(name)
    return names

def contentsWithPatternsFromFolder(folder, patterns):
    contents = os.listdir(folder)
    paths = []
    for content in contents:
        matches = True
        for pattern in patterns:
            if not pattern in content:
                matches = False
                break

        if matches:
            paths.append(content)

    return paths

def contentsWithRegexpFromFolder(folder, regexp):
    contents = os.listdir(folder)
    paths = [x for x in contents if regexp.match(x)] if regexp else contents
    return paths

def removeNameWithPatterns(list, patterns):
    found = None
    for name in list:
        matches = True
        for pattern in patterns:
            if not pattern in name:
                matches = False
                break

        if matches:
            found = name
            break
    return found

def removeNameEndingWith(list, pattern):
    found = None
    for name in list:
        if name.endswith(pattern):
            found = name
            break
    return found

def removeNamesWithPatterns(list, patterns):
    found = []
    for name in list:
        matches = True
        for pattern in patterns:
            if not pattern in name:
                matches = False
                break

        if matches:
            found.append(name)
    return found

class FileIterator(object):
    def __init__(self, path, header=None, compressed = False):
        self.path = path
        self.compressed = compressed
        self.header = header

    def iterate(self,callback=None):
        if self.compressed:
            with gzip.open(self.path, 'rb') as file_object:
                self._iterateOverFile(file_object, callback)
        else:
            with open(self.path, 'rb') as file_object:
                self._iterateOverFile(file_object, callback)

    def _iterateOverFile(self, file_object, callback):
        if self.header is not None:
            line = file_object.readline().strip("\n")
            assert line == self.header

        self._processFile(file_object, callback)

    def _processFile(self, file_object, callback):
        if callback is not None:
            for i,line in enumerate(file_object):
                callback(i, line)

class CSVFileIterator(FileIterator):
    def _processFile(self, file_object, callback):
        if callback is not None:
            reader = csv.reader(file_object, delimiter=" ", quotechar='"')
            for i,row in enumerate(reader):
                callback(i, row)

def samplesInputPath(path):
    samples_file = contentsWithPatternsFromFolder(path, ["samples"])[0]
    samples_path = os.path.join(path, samples_file)
    return  samples_path