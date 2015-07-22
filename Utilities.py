__author__ = 'heroico'

import os

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