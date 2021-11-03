import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog



class MainWindowManager():
    def __init__(self):
        self.curNotesPath = ''
        content = tk.Frame(window)
        content.pack(fill = 'both', expand = True)


        # Directory Info Area
        infoFrame = tk.Frame(content)
        fr_buttons = tk.Frame(infoFrame, relief=tk.RAISED, bd=2)
        btn_open = tk.Button(fr_buttons, text="Open Notes Directory", command=self.openDir)
        self.currentDirLabel = tk.Label(infoFrame, text = self.curNotesPath)
        fr_buttons.grid()
        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.currentDirLabel.grid(row=0, column=1, sticky="ew", padx=5)
        infoFrame.pack(side = 'top', fill = 'both')

        # Text Area
        self.openFileArea = tk.Text(content)
        textScrollBar = tk.Scrollbar(content, command=self.openFileArea.yview)
        self.openFileArea['yscrollcommand'] = textScrollBar.set
        textScrollBar.pack(side = 'right', fill = 'y')
        self.openFileArea.pack(side = 'right', fill = 'both', expand = True)


        # File Tree Area
        self.fileTreeFrame = tk.Frame(content)
        self.fileTreeFrame.pack(side = 'left', fill = 'both', expand = True)
        yFrame = tk.Frame(self.fileTreeFrame)
        self.tree = ttk.Treeview(yFrame)
        ysb = ttk.Scrollbar(yFrame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.heading('#0', text=self.curNotesPath, anchor='w')
        self.tree.bind("<Double-1>", self.onFileTreeDoubleClick)
        self.tree.pack(side = 'left', fill = 'both', expand = True)
        ysb.pack(side = 'left', fill = 'y')
        yFrame.pack(side = 'top', fill = 'both', expand = True)
        self.setupFileTree()

    def openDir(self):
        filepath = filedialog.askdirectory()
        if not filepath:
            return
        self.curNotesPath = filepath
        window.title(f"Notes - {filepath}")
        self.currentDirLabel.configure(text = "Current Directory: " + self.curNotesPath)
        self.setupFileTree()

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

    def onFileTreeDoubleClick(self, event):
        item = self.tree.selection()[0]
        fullPath = "" 
        while item != "":
            parent = self.tree.item(item)['text']
            if fullPath == "":
                fullPath = parent
            else:
                fullPath = os.path.join(parent, fullPath) 
            item = self.tree.parent(item)

        if os.path.isdir(fullPath):
            return
        self.setPreviewText(''.join(open(fullPath, 'r', encoding = "utf-8", errors = "ignore").readlines()))

    def setPreviewText(self, textToDisplay):
        self.openFileArea.config(state = "normal")
        self.openFileArea.delete(1.0, "end")
        self.openFileArea.insert(1.0, textToDisplay)
        self.openFileArea.config(state = "disabled")

if __name__ == "__main__":
    window = tk.Tk()

    window.title("Notes")
    MainWindowManager()

    window.mainloop()


