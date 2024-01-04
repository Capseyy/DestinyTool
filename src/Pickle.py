import pickle
import tkinter.messagebox



def WritePickle(Dict,Name,CWD):
    with open(CWD+"/Storage/"+Name+".pkl", 'wb') as fp:
        pickle.dump(Dict, fp)
        fp.close()
   


def GetStringDict(CWD):
    try:
        fp=open(CWD+"/Storage/Strings.pkl","rb")
    except FileNotFoundError:
        tkinter.messagebox.showinfo("Warning","String Database not created")
        return {}
    else:
        person = pickle.load(fp)
        fp.close()
        return person
    
def GetFnvDict(CWD):
    try:
        fp=open(CWD+"/Storage/FNVs.pkl","rb")
    except FileNotFoundError:
        tkinter.messagebox.showinfo("Warning","FNV Database not created")
        return {}
    else:
        person = pickle.load(fp)
        fp.close()
        return person

def GetWIDDict(CWD):
    try:
        fp=open(CWD+"/Storage/WIDs.pkl","rb")
    except FileNotFoundError:
        tkinter.messagebox.showinfo("Warning","WorldID Database not created")
        return {}
    else:
        person = pickle.load(fp)
        fp.close()
        return person
