import os
import re
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.font as tkFont
import subprocess, platform
from datetime import datetime
from search import Search



preferencesFile = './preferences.py'
defaultDirPrefKey = 'defaultDir' 

class MainWindowManager():
    def __init__(self, root):
        self.root = root
        self.preferences = {}
        if os.path.exists(preferencesFile):
            with open(preferencesFile, 'r') as prefInput:
                self.preferences = eval(prefInput.read())

        self.curNotesPath = ''
        if defaultDirPrefKey in self.preferences:
            self.curNotesPath = self.preferences[defaultDirPrefKey]

        self.searchEngine = None

        content = tk.Frame(window)
        content.pack(fill = 'both', expand = True)


        
        # Directory Info Area
        infoFrame = tk.Frame(content)
        fr_buttons = tk.Frame(infoFrame, relief=tk.RAISED, bd=2)
        btn_open = tk.Button(fr_buttons, text="Open Notes Directory", command=self.openDir)
        self.currentDirLabel = tk.Label(fr_buttons, text = "Current directory: " + self.curNotesPath)
        fr_buttons.grid()
        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.currentDirLabel.grid(row=0, column=1, sticky="ew", padx=5)
        self.setDefaultBtn = tk.Button(fr_buttons, text = "Set as Default", command = self.setDefaultNotesDir, state = 'disabled')
        self.setDefaultBtn.grid(row=0, column=2, sticky="ew", padx=5)
        infoFrame.pack(side = 'top', fill = 'x')

        # Text Area
        self.textFont = tkFont.Font(family="Calibri", size=16)
        openFileFrame = tk.Frame(content) 
        self.fileNameLabel = tk.Label(openFileFrame, text = "", font = self.textFont)
        self.fileNameLabel.pack(side = 'top', fill = 'x')
        fileButtonsFrame = tk.Frame(openFileFrame)
        openInEditorBtn = tk.Button(fileButtonsFrame, text = "Open in Editor", command = self.openFile)
        openInEditorBtn.pack(side = "left")
        openContainingFolder = tk.Button(fileButtonsFrame, text = "Open Containing Folder", command = self.openDir)
        openContainingFolder.pack(side = "left")
        zoomPlus = tk.Button(fileButtonsFrame, text = "+", command = self.increaseFontSize)
        zoomPlus.pack(side = "right")
        zoomMinus = tk.Button(fileButtonsFrame, text = "-", command = self.decreaseFontSize)
        zoomMinus.pack(side = "right")
        self.refreshFile = tk.Button(fileButtonsFrame, text = "Reload File", command = self.loadFile, state = 'disabled')
        self.refreshFile.pack(side = "right")
        newNoteBtn = tk.Button(fileButtonsFrame, text = "Add New Note", command = self.newNoteWindow)
        newNoteBtn.pack(side = "left")
        tagsFrame = tk.Frame(openFileFrame)
        tk.Label(tagsFrame, text = "TagList: ").pack(side = 'left')
        tagList = ['tagtest1', 'tagtest2', 'tagtest3']
        for t in tagList:
            curTagFrame = tk.Frame(tagsFrame)
            curTagFrame.pack(side = 'left')
            tempLabel = tk.Label(curTagFrame, text = t)
            #tempBtn = tk.Button(curTagFrame, text = 'x')
            tempLabel.pack(side = 'left')
            #tempBtn.pack(side = 'left')

        fileButtonsFrame.pack(side = 'top', fill = 'x')
        tagsFrame.pack(side = 'top', fill = 'x')
        self.openFileArea = tk.Text(openFileFrame, font = self.textFont)
        self.openFileArea.pack(side = 'top', fill = 'both', expand = True)
        textScrollBar = tk.Scrollbar(content, command=self.openFileArea.yview)
        self.openFileArea['yscrollcommand'] = textScrollBar.set
        textScrollBar.pack(side = 'right', fill = 'y')
        openFileFrame.pack(side = 'right', fill = 'both', expand = True)


        # File Tree Area
        FileArea = tk.Frame(content)
        FileArea.pack(side = 'left', fill = 'both', expand = True)
        # Search buttons
        searchFrame = tk.Frame(FileArea, padx = 5)
        searchFrame.pack(side = 'top', fill = 'x')
        self.searchArea = tk.Entry(searchFrame)
        self.searchArea.pack(side = 'left', fill = 'x', expand = True)
        self.searchArea.bind('<Return>', self.searchAllFiles)
        clearSearchBtn = tk.Button(searchFrame, text = 'x', command = self.hideSearchResultsFrame)
        clearSearchBtn.pack(side = 'left')
        searchBtn = tk.Button(searchFrame, text = "search", command = self.searchAllFiles)
        searchBtn.pack(side = 'left')
        # Search Results
        self.searchResultsListArea = tk.Frame(FileArea)
        self.searchResultsList = tk.Listbox(self.searchResultsListArea)
        self.searchResultsList.pack(side = 'left', fill = 'both', expand = True)
        # File Tree
        self.fileTreeFrame = tk.Frame(FileArea)
        self.hideSearchResultsFrame()
        yFrame = tk.Frame(self.fileTreeFrame)
        self.tree = ttk.Treeview(yFrame)
        ysb = ttk.Scrollbar(yFrame, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self.fileTreeFrame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree.heading('#0', text=self.curNotesPath, anchor='w')
        self.tree.bind("<Double-1>", self.onFileTreeDoubleClick)
        self.tree.pack(side = 'left', fill = 'both', expand = True)
        ysb.pack(side = 'left', fill = 'y')
        yFrame.pack(side = 'top', fill = 'both', expand = True)
        xsb.pack(side = 'top', fill = 'x')
        self.setupFileTree()

    def openDir(self):
        filepath = filedialog.askdirectory()
        if not filepath:
            return
        self.curNotesPath = filepath
        window.title(f"Notes - {filepath}")
        self.currentDirLabel.configure(text = "Current Directory: " + self.curNotesPath)
        self.setupFileTree()
        if self.preferences[defaultDirPrefKey] != self.curNotesPath:
            self.setDefaultBtn.configure(state = 'normal')
        else:
            self.setDefaultBtn.configure(state = 'disabled')

    def setupFileTree(self):
        if self.curNotesPath == "":
            return
        
        self.tree.delete(*self.tree.get_children())

        abspath = os.path.abspath(self.curNotesPath)
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.processDirectory(root_node, abspath)

        self.searchEngine = Search(self.curNotesPath)
        

    def processDirectory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.processDirectory(oid, abspath)

    def getFullPathOfTreeSelection(self):
        try:
            selection = self.tree.selection()[0]
        except IndexError:
            return self.curNotesPath, ''

        item = selection
        fullPath = "" 
        while item != "":
            parent = self.tree.item(item)['text']
            if fullPath == "":
                fullPath = parent
            else:
                fullPath = os.path.join(parent, fullPath) 
            item = self.tree.parent(item)
        return fullPath, self.tree.item(selection)['text']

    def onFileTreeDoubleClick(self, event):
        self.loadFile()

    def setPreviewText(self, textToDisplay):
        self.openFileArea.config(state = "normal")
        self.openFileArea.delete(1.0, "end")
        self.openFileArea.insert(1.0, textToDisplay)
        self.openFileArea.config(state = "disabled")
        self.refreshFile.configure(state = 'normal')

    def increaseFontSize(self):
        self.textFont.configure(size = self.textFont['size']+2) 

    def decreaseFontSize(self):
        self.textFont.configure(size = self.textFont['size']-2) 

    def setDefaultNotesDir(self):
        self.setDefaultBtn.configure(state = 'disabled')
        self.preferences[defaultDirPrefKey] = self.curNotesPath
        with open(preferencesFile, 'w') as prefFile:
            prefFile.write(str(self.preferences))

    def openDir(self):
        if self.curNotesPath == "":
            return
        filepath, fileName = self.getFullPathOfTreeSelection()
        filepath = filepath.removesuffix(fileName)
        if filepath == "":
            return
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))

    def openFile(self):
        filepath, _ = self.getFullPathOfTreeSelection()
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))

    def loadFile(self):
        fullPath, fileName = self.getFullPathOfTreeSelection()

        if os.path.isdir(fullPath):
            return
        self.setPreviewText(''.join(open(fullPath, 'r', encoding = "utf-8", errors = "ignore").readlines()))
        self.fileNameLabel.configure(text = fileName)

    def newNoteWindow(self):
        self.newNoteWindowToplevel = tk.Toplevel()
        self.newNoteWindowToplevel.attributes("-topmost", True)
        self.newNoteWindowToplevel.bind('<Return>', self.makeNewNoteCustomName)

        #windowContent = tk.Frame(self.newNoteWindowToplevel)
        customNameFrame = tk.Frame(self.newNoteWindowToplevel)
        #customNameFrame = tk.Frame(windowContent)
        customNameFrame.pack(side = 'top')
        self.newNoteName = tk.Text(customNameFrame, width = 30,  height = 1)
        self.newNoteName.focus_set()
        self.newNoteName.pack(side = "left",  fill = 'x')
        okBtn = tk.Button(customNameFrame, text = "OK", command = self.makeNewNoteCustomName)
        okBtn.pack(side = 'left')
        customNameFrame.pack(side = 'top')
        #timestampBtn = tk.Button(windowContent, text = "TimeStamp As Title", command = self.makeNewNoteDefaultName)
        timestampBtn = tk.Button(self.newNoteWindowToplevel, text = "TimeStamp As Title", command = self.makeNewNoteDefaultName)
        timestampBtn.pack(side = 'top')

        w = self.newNoteWindowToplevel.winfo_reqwidth()
        h = self.newNoteWindowToplevel.winfo_reqheight()
        ws = self.newNoteWindowToplevel.winfo_screenwidth()
        hs = self.newNoteWindowToplevel.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.newNoteWindowToplevel.geometry('%dx%d+%d+%d' % (300, 60, x, y))
        self.newNoteWindowToplevel.title("New Note")
        self.newNoteWindowToplevel.focus_force()

    def makeNewNoteDefaultName(self):
        time = datetime.now()
        name = time.strftime("%d-%m-%Y@%H%M%S") + '.md'
        self.makeNewNote(name)
        self.newNoteWindowToplevel.destroy() 
        self.setupFileTree()
        self.setPreviewText(''.join(open(os.path.join(self.curNotesPath, name), 'r', encoding = "utf-8", errors = "ignore").readlines()))

    def makeNewNoteCustomName(self, event = None):
        name = self.newNoteName.get(1.0, 'end-1c')
        name = os.path.normpath(name.replace('\n', '')) + '.md'
        if name != "":
            self.makeNewNote(name)
        self.newNoteWindowToplevel.destroy() 
        self.setupFileTree()
        if name != "":
            self.setPreviewText(''.join(open(os.path.join(self.curNotesPath, name)).readlines()))

    def makeNewNote(self, name):
        time = datetime.now()
        timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
        with open(os.path.join(self.curNotesPath, name), 'w') as newNote:
            newNote.write('# ' + name + '\n')
            newNote.write(timestamp +'\n\n')


    def searchAllFiles(self, event = None):
        searchTerm = self.searchArea.get().strip()
        files = self.searchEngine.search(searchTerm)

        self.searchResultsList.delete(0, 'end')
        for f in files:
            self.searchResultsList.insert('end', f)
        if len(files) == 0:
            self.searchResultsList.insert('end', "\'" + searchTerm + "'" + ' not found')

        self.showSearchResultsFrame()

    def showSearchResultsFrame(self):
        self.fileTreeFrame.pack_forget()
        self.searchResultsListArea.pack(side = "left", fill = 'both', expand = True)

    def hideSearchResultsFrame(self):
        self.searchResultsListArea.pack_forget()
        self.fileTreeFrame.pack(side = "left", fill = 'both', expand = True)


if __name__ == "__main__":
    window = tk.Tk()

    window.title("Notes")
    MainWindowManager(window)

    window.mainloop()


