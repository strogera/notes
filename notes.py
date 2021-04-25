import argparse
import sys
from os import path
from os import walk
from collections import defaultdict

parser = argparse.ArgumentParser(description='Manage your notes.')
parser.add_argument('-d', '--directory', dest='directory', help='Specify the directory of the notes')
args = parser.parse_args()
if not path.exists(args.directory) or not path.isdir(args.directory):
    print('Not a valid directory')
    exit

tagChars = '-_abcdefghijklmnopqrstuvwxyz0123456789'
filesOfTag = defaultdict(list)
tagsOfFile = defaultdict(list)

untagged = 'untagged'
for (dirpath, dirnames, filenames) in walk(args.directory):
    for f in filenames:
        if '.md' in f or '.txt' in f:
            filename = dirpath + '/' + f
            with open(filename, 'r') as note:
                tagged = False 
                for line in note:
                    for i in range(len(line)):
                        if line[i] == '#':
                            try:
                                if line[i+1] in tagChars:
                                    tag = '#'
                                    for x in line[i+1:]:
                                        if x not in tagChars:
                                            if tag !='#':
                                                tag = tag.lower()
                                                tagged = True
                                                filesOfTag[tag].append(filename)
                                                tagsOfFile[filename].append(tag)
                                                break
                                        else:
                                            tag += x
                                else:
                                    continue
                            except:
                                pass
                if not tagged:
                    filesOfTag[untagged].append(filename)
                    tagsOfFile[filename].append(untagged)

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

def makeMarkdownLink(filename):
    return '['+getFileNameFromPathNoExtention(filename)+']('+filename.replace(' ', '%5C')+')'
    return '['+getFileNameFromPathNoExtention(filename)+']('+filename.replace(' ', '%20')+')'

def printAllFilesPerTag():
    for tag in filesOfTag:
        print('# '+tag)
        print()
        for l in filesOfTag[tag]:
            print('* '+ makeMarkdownLink(l))
        print()

def printAllFilesWithTags():
    for file in tagsOfFile:
        print('# ', makeMarkdownLink(file))
        for tag in tagsOfFile[file]:
            print(tag)
        print()

printAllFilesWithTags()
