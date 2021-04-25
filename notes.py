import argparse
import sys
from os import path
from os import walk
from collections import defaultdict

filesOfTag = defaultdict(list)
tagsOfFile = defaultdict(list)
untagged = 'untagged'
tagChars = '-_abcdefghijklmnopqrstuvwxyz0123456789'

def getTagsFromString(s):
    tagsFound = []
    tag = ''
    i = 0
    while i < len(s) - 1:
        currentChar = s[i].lower()
        nextChar = s[i+1].lower()

        if not tag:
            if currentChar == '#' and nextChar in tagChars:
                tag = '#'
        else:
            if currentChar in tagChars:
                tag += currentChar
            else:
                tagsFound.append(tag)
                tag = ''
        i += 1
    if tag:
        tagsFound.append(tag)
    return tagsFound

def findTagsInFile(fullpath):
    with open(fullpath, 'r') as note:
        tagged = False 
        curTags = []
        for line in note:
            curTags += getTagsFromString(line)

        if not curTags:
            filesOfTag[untagged].append(fullpath)
            tagsOfFile[fullpath].append(untagged)
        else:
            for tag in curTags:
                filesOfTag[tag].append(fullpath)
                tagsOfFile[fullpath].append(tag)


def getFileNameFromPath(path):
    name = ''
    for c in path[::-1]:
        if c!='/':
            name += c
        else:
            break
    return name[::-1]


def removeExtension(filename):
    name = filename[::-1]
    for c in name:
        name = name[1:]
        if c == '.':
            break
    return name[::-1]


def getFileNameFromPathNoExtention(filename):
    return getFileNameFromPath(removeExtension(filename))


def makeMarkdownLink(filename, espaceSpaces=True):
    if espaceSpaces:
        return '['+getFileNameFromPathNoExtention(filename)+']('+filename.replace(' ', '\\ ')+')'
    else:
        return '['+getFileNameFromPathNoExtention(filename)+']('+filename+')'


def printAllFilesPerTag():
    print('# Tag - Files List\n')
    for tag in filesOfTag:
        print('## '+tag)
        print()
        uniqueFileList = set(filesOfTag[tag])
        for f in uniqueFileList:
            print('* '+ makeMarkdownLink(f))
        print()

def printAllFilesWithTags():
    print('# File - Tags List\n')
    for file in tagsOfFile:
        print('## ', makeMarkdownLink(file))
        uniqueTagList = set(tagsOfFile[file])
        for tag in uniqueTagList:
            print('* ' + tag)
        print()

parser = argparse.ArgumentParser(description='Manage your notes.')
parser.add_argument('-d', '--directory', dest='directory', help='Specify the directory of the notes')
args = parser.parse_args()
if not path.exists(args.directory) or not path.isdir(args.directory):
    print('Not a valid directory')
    exit


for (dirpath, dirnames, filenames) in walk(args.directory):
    for f in filenames:
        if '.md' in f or '.txt' in f:
            fullpath = dirpath + '/' + f
            findTagsInFile(fullpath)

#printAllFilesWithTags()
printAllFilesPerTag()
