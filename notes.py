import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.font as tkFont
import subprocess, platform



preferencesFile = './preferences.py'
defaultDirPrefKey = 'defaultDir' 

class MainWindowManager():
    def __init__(self):
        self.preferences = {}
        if os.path.exists(preferencesFile):
            with open(preferencesFile, 'r') as prefInput:
                self.preferences = eval(prefInput.read())

        self.curNotesPath = ''
        if defaultDirPrefKey in self.preferences:
            self.curNotesPath = self.preferences[defaultDirPrefKey]

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
        infoFrame.pack(side = 'top', fill = 'both')

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
        newNoteBtn = tk.Button(fileButtonsFrame, text = "Add New Note")
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
        self.fileTreeFrame = tk.Frame(content)
        self.fileTreeFrame.pack(side = 'left', fill = 'both', expand = True)
        yFrame = tk.Frame(self.fileTreeFrame)
        self.tree = ttk.Treeview(yFrame)
        ysb = ttk.Scrollbar(yFrame, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self.fileTreeFrame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree.heading('#0', text=self.curNotesPath, anchor='w')
        self.tree.bind("<Double-1>", self.onFileTreeDoubleClick)
        self.tree.pack(side = 'left', fill = 'both', expand = True)
        ysb.pack(side = 'left', fill = 'y')
        searchFrame = tk.Frame(self.fileTreeFrame, padx = 5)
        searchFrame.pack(side = 'top')
        searchArea = tk.Text(searchFrame, height = 1, width = 30)
        searchArea.pack(side = 'left', fill = 'x')
        searchArea.insert(1.0, "placeholder")
        clearSearchBtn = tk.Button(searchFrame, text = 'x')
        clearSearchBtn.pack(side = 'left')
        searchBtn = tk.Button(searchFrame, text = "search")
        searchBtn.pack(side = 'left')
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
        

    def processDirectory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.processDirectory(oid, abspath)

    def getFullPathOfTreeSelection(self):
        selection = self.tree.selection()[0]
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
        filepath = self.curNotesPath
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


if __name__ == "__main__":
    window = tk.Tk()

    window.title("Notes")
    MainWindowManager()

    window.mainloop()


