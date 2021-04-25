import argparse
import sys
from os import path
from os import walk
from collections import defaultdict

parser = argparse.ArgumentParser(description='Manage your notes.')
parser.add_argument('-d', '--directory', dest='directory', help='Specify the directory of the notes')
args = parser.parse_args()
print(args.directory)
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

for tag in filesOfTag:
    print('# '+tag)
    print()
    for l in filesOfTag[tag]:
        print('* ['+'placeholder'+']('+l.replace(' ', '%5C')+')')
        #print('* ['+'placeholder'+']('+l.replace(' ', '%20')+')')
    print()

#for file in tagsOfFile:
    #print('# ', file)
    #for tag in tagsOfFile[file]:
        #print(tag)
    #print()
