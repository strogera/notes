import argparse
import sys
from os import path
from os import walk
from os import system
from collections import defaultdict
from datetime import datetime

filesOfTag = defaultdict(list)
tagsOfFile = defaultdict(list)
untagged = 'untagged'
tagChars = '-_abcdefghijklmnopqrstuvwxyz0123456789'
time = datetime.now()
defaultNewFileName = time.strftime("%d/%m/%Y-%H:%M:%S")

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

def readNotesDirectory(args):
    if not path.exists(args.directory) or not path.isdir(args.directory):
        print('Not a valid directory')
        exit

    for (dirpath, dirnames, filenames) in walk(args.directory):
        for f in filenames:
            if '.md' in f or '.txt' in f:
                fullpath = dirpath + '/' + f
                findTagsInFile(fullpath)

parser = argparse.ArgumentParser(description='Manage your notes.')
parser.add_argument('-d', '--directory', dest='directory', required=True, help='Specify the directory of the notes')
parser.add_argument('-n', '--new', dest='newNoteName', help='Start a new Note. Saves it in the -d directory')
parser.add_argument('-lt', '--list-tags', dest='listTags', action='store_true', help='List available tags')
parser.add_argument('-ln', '--list-notes', dest='listNotes', action='store_true', help='List available notes')
parser.add_argument('-t', '--tag-find', dest='tagToFind', help='Find all files with tag')
args = parser.parse_args()

#printAllFilesWithTags()
#printAllFilesPerTag()
if args.newNoteName:
    newNoteFullPath = args.directory + '/' + args.newNoteName
    print(newNoteFullPath)
    with open(newNoteFullPath, 'w') as newNote:
        newNote.write('# ' + args.newNoteName)
    system('vim ' + newNoteFullPath) 
readNotesDirectory(args)

if args.listTags:
    print("# Available tags\n")
    availableTags = list(filesOfTag.keys())
    for tag in sorted(availableTags):
        if tag == untagged:
            continue
        print('* ' + tag)

if args.listNotes:
    print("# Available notes\n")
    availableNotes = list(tagsOfFile.keys())
    for note in sorted(availableNotes):
        print('* ' + makeMarkdownLink(note))

if args.tagToFind:
    tagToFind = args.tagToFind
    if tagToFind[0] != '#':
        tagToFind = '#' + tagToFind
    if tagToFind not in filesOfTag:
        print('Tag doesn\'t exist')
    else:
        print('# ' + tagToFind + '\n')
        for file in filesOfTag[tagToFind]:
            print('* ' + makeMarkdownLink(file))

