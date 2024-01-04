from tkinter import *
from tkinter import ttk
from functools import partial
from Strings import StringGen, FnvGen
from Activity import ActivityListGen, GetEncounterList, ExtractEncounter
import os,sys,Util,binascii,gf,ast,common,Pickle
from Entity import ExtractEntity
from common import ParseTag
from Package import DumpTag

class Window:
    def __init__(self,CWD,PkgCache):
        self.GlobalStringDict=Pickle.GetStringDict(CWD)
        self.FnvDict=Pickle.GetFnvDict(CWD)
        self.root=Tk()
        self.root.title("The Tech")
        self.root.geometry("1200x600")
        self.CWD=CWD
        self.DevNameDict={}
        self.ActList={}
        self.PackageCache=PkgCache
        
    
    def MainWindow(self):
        print(self.CWD)
        for widget in self.root.winfo_children():
            widget.destroy()
        bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
        label1 = Label(self.root, image = bg)
        label1.pack()
        String = Button(self.root, text="Generate String DB", height=1, width=15,command=partial(CollectStrings,self))
        String.place(x=500, y=125)
        Fnv = Button(self.root, text="Generate FNV DB(long)", height=1, width=15,command=partial(CollectFnvs,self))
        Fnv.place(x=650, y=125)
        Activity = Button(self.root, text="Activites", height=1, width=15,command=partial(ActivityListGen,self))
        Activity.place(x=500, y=225)
        Quit = Button(self.root, text="Quit", height=1, width=15,command=partial(QuitOut))
        Debug = Button(self.root, text="Debug Menu", height=1, width=15,command=partial(self.DebugMenu))
        ClearMap = Button(self.root, text="Clear Maps", height=1, width=15,command=partial(Util.ClearMaps,self.CWD))
        ClearMap.place(x=1000, y=430)
        Debug.place(x=1000, y=100)
        Quit.place(x=100, y=510)
        self.root.mainloop()
    
    def DebugMenu(self):
        global lst,combo_box
        lst=[]
        for widget in self.root.winfo_children():
            widget.destroy()
        bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
        label1 = Label(self.root, image = bg)
        label1.pack()
        combo_box = ttk.Combobox(self.root,height=20, width=40)
        combo_box['values'] = []
        combo_box.bind('<KeyRelease>', check_input)
        combo_box.place(x=500, y=125)
        Activity = Button(self.root, text="Extract Entity", height=1, width=15,command=partial(DumpEntity,combo_box,self.PackageCache))
        Activity.place(x=500, y=175)
        TagParse = Button(self.root, text="Parse Tag", height=1, width=15,command=partial(ParseTag,combo_box,self.PackageCache,self.GlobalStringDict,self.FnvDict))
        TagParse.place(x=600, y=175)
        TagParse = Button(self.root, text="Dump Tag", height=1, width=15,command=partial(DumpTag,combo_box,self.PackageCache))
        TagParse.place(x=600, y=225)
        EntrySearch = Button(self.root, text="Search Bungie Files", height=1, width=20,command=partial(common.SearchVal,combo_box))
        EntrySearch.place(x=500, y=375)
        Back = Button(self.root, text="Back", height=1, width=15,command=partial(self.MainWindow))
        Back.place(x=10, y=10)
        Clear = Button(self.root, text="Clear Audio", height=1, width=15,command=partial(Util.ClearAudio,self.CWD))
        Clear.place(x=1000, y=550)
        ClearOut = Button(self.root, text="Clear Out", height=1, width=15,command=partial(Util.ClearDir,self.CWD))
        ClearOut.place(x=1000, y=510)
        ClearTex = Button(self.root, text="Clear Textures", height=1, width=15,command=partial(Util.ClearTextures,self.CWD))
        ClearTex.place(x=1000, y=470)
        ClearMap = Button(self.root, text="Clear Maps", height=1, width=15,command=partial(Util.ClearMaps,self.CWD))
        ClearMap.place(x=1000, y=430)
        ClearScript = Button(self.root, text="Clear Scripts", height=1, width=15,command=partial(Util.ClearScripts,self.CWD))
        ClearScript.place(x=1000, y=390)
        self.root.mainloop()
    
    def ActivityMenu(self):
        global lst, combo_box
        lst=[]
        for key, value in self.ActList.items():
            lst.append(key)
        for widget in self.root.winfo_children():
            widget.destroy()
        bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
        label1 = Label(self.root, image = bg)
        label1.pack()
        combo_box = ttk.Combobox(self.root,height=20, width=50)
        combo_box['values'] = lst[::-1]
        combo_box.bind('<KeyRelease>', check_input)
        combo_box.place(x=500, y=125)
        Activity = Button(self.root, text="Extract Maps", height=1, width=15,command=partial(dummy))
        Activity.place(x=500, y=175)
        Phase = Button(self.root, text="Extract Encounters", height=1, width=15,command=partial(GetEncounterList,self,combo_box,self.ActList))
        Phase.place(x=600, y=225)
        Back = Button(self.root, text="Back", height=1, width=15,command=partial(self.MainWindow))
        Back.place(x=10, y=10)
        self.root.mainloop()

    def EncounterMenu(self):
        global lst, combo_box
        lst=[]
        for widget in self.root.winfo_children():
            widget.destroy()
        for key, value in self.DevNameDict.items():
            lst.append(key)
        bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
        label1 = Label(self.root, image = bg)
        label1.pack()
        combo_box = ttk.Combobox(self.root,height=20, width=50)
        combo_box['values'] = lst
        combo_box.bind('<KeyRelease>', check_input)
        combo_box.place(x=500, y=125)
        Phase = Button(self.root, text="Extract Encounter", height=1, width=15,command=partial(ExtractEncounter,combo_box,self.DevNameDict,self.PackageCache))
        Phase.place(x=500, y=225)
        Comb = Button(self.root, text="Extract Combatant Table", height=1, width=15,command=partial(dummy))
        Comb.place(x=600, y=225)
        Vars= Button(self.root, text="Extract Variables", height=1, width=15,command=partial(dummy))
        Vars.place(x=500, y=325)
        Vars2= Button(self.root, text="Parse Phase", height=1, width=15,command=partial(dummy))
        Vars2.place(x=600, y=325)
        Back = Button(self.root, text="Back", height=1, width=15,command=partial(self.ActivityMenu))
        Back.place(x=10, y=10)
        self.root.mainloop()


def check_input(event):
    global lst, combo_box
    value = event.widget.get()
    if value == '':
        combo_box['values'] = lst
    else:
        data = []
        for item in lst:
            if value.lower() in item.lower():
                data.append(item)
        combo_box['values'] = data

def QuitOut():
    sys.exit()
def CollectFnvs(Window):
    FnvDict=FnvGen()
    Window.FnvDict=FnvDict
    Window.MainWindow()
def CollectStrings(Window):
    GlobalStringDict=StringGen()
    Window.GlobalStringDict=GlobalStringDict
    Window.MainWindow()
def DumpEntity(combo_box,PackageCache):
    string=combo_box.get()
    Hash=ast.literal_eval("0x"+binascii.hexlify(bytes(gf.hex_to_little_endian(string))).decode('utf-8'))
    Tag=common.TagHash(Hash)
    ExtractEntity(Tag,PackageCache)
def dummy():
    u=1
