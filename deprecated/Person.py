__author__ = 'heroico'

import csv

class STFS(object):
    """sample file table format"""
    ID = 0
    POP = 1
    GROUP = 2
    SEX = 3

class Person(object):
    """A person."""
    def __init__(self):
        self.id = None
        self.population = None
        self.group = None
        self.sex = None

    def toTextLine(self):
        return " ".join([self.id, self.population, self.group, self.sex])

    @classmethod
    def loadPersonFromSampleRow(cls, row):
        person = Person()
        person.id = row[STFS.ID]
        person.population = row[STFS.POP]
        person.group = row[STFS.GROUP]
        person.sex = row[STFS.SEX]
        return  person

    @classmethod
    def loadPersonFromSampleRowIfEuropean(cls, row):
        person = None
        if row[STFS.GROUP] == "EUR":
            person = Person.loadPersonFromSampleRow(row)
        return person

    @classmethod
    def filterSamples(cls, input, output, row_delimiter=' ', skip_header=True):
        filtered = []
        with open(input, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=row_delimiter, quotechar='"')
            for row in reader:
                if skip_header and reader.line_num == 1:
                    continue

                person = Person.loadPersonFromSampleRowIfEuropean(row)
                if person is not None:
                    filtered.append(person)

        with open(output, 'w+') as output_file:
            output_file.write(" ".join(["ID", "POP", "GROUP", "SEX"])+"\n")
            for person in filtered:
                output_file.write(person.toTextLine()+"\n")

    @classmethod
    def allPeople(cls, input, delim=' ', skip_header=True):
        people = []
        with open(input, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=delim, quotechar='"')
            for row in reader:
                if skip_header and reader.line_num == 1:
                    continue
                person = Person.loadPersonFromSampleRow(row)
                people.append(person)
        return people

    @classmethod
    def peopleByIdFromFile(cls, input):
        people_by_id = {}
        with open(input, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=' ', quotechar='"')
            for row in reader:
                if reader.line_num == 1:
                    continue

                person = Person.loadPersonFromSampleRow(row)
                people_by_id[person.id] = person
        return people_by_id
