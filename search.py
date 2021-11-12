import os
import bisect

class SearchDataEntry:
    def __init__(self, filePath, word):
        self.filePath = filePath
        self.word = word.lower()

    def __lt__(self, other):
        return self.word < other.word

class Search:
    def __init__(self, directory):
        self.searchData = []
        self.readDir(directory)

    def readDir(self, dire):
        for p, _, files in os.walk(dire):
            for f in files:
                curFilePath = os.path.join(p, f)
                with open(curFilePath, 'r', encoding = "utf-8", errors = "ignore") as curFile:
                    for line in  curFile.readlines():
                        for word in line.strip().split(' '):
                            if word != '':
                                bisect.insort(self.searchData, SearchDataEntry(curFilePath, word))

    def indexOfElementInSearchData(self, elem):
        i = bisect.bisect_left(self.searchData, elem)
        if i != len(self.searchData) and self.searchData[i].word.startswith(elem.word):
            return i
        return -1

    def search(self, term):
        term = term.lower()
        filepaths = set()
        i = self.indexOfElementInSearchData(SearchDataEntry('', term))

        while self.searchData[i].word.startswith(term):
            filepaths.add(self.searchData[i].filePath)
            i += 1
        return filepaths
