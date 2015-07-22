__author__ = 'heroico'

import os
import gzip

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
            with gzip.open(self.path, 'rb') as file:
                self._iterateOverFile(file, callback)
        else:
            with open(self.path, 'rb') as file:
                self._iterateOverFile(file, callback)

    def _iterateOverFile(self, file, callback):
        for i,line in enumerate(file):
            stripped = line.strip("\n")
            if i==0 and self.header is not None:
                assert stripped == self.header
                continue

            if callback is not None:
                callback(stripped)
