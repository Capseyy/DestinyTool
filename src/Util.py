from tkinter import *
from tkinter import ttk
from functools import partial
import os,sys,ast,gf,Package
import multiprocessing as mp
import Package
global PackageCache,H64Data,Cwd

def ClearScripts(CWD):
    for file in os.listdir(os.getcwd()+"/ExtractedFiles/Scripts"):
        os.remove(CWD+"/ExtractedFiles/Scripts/"+file)
def ClearDir(CWD):
    t_pool=mp.Pool(mp.cpu_count())
    _args = [(File,"L") for File in os.listdir(CWD+"/out")]
    t_pool.starmap(
        DelFile, 
        _args)
def DelFile(File,Null):
    if File != "audio":
        os.remove(os.getcwd()+"/out/"+File)
def ClearMaps(CWD):
    #for file in os.listdir(CWD+"/Maps/Statics"):
    #    os.remove(CWD+"/Maps/Statics/"+file)
    for file in os.listdir(CWD+"/Maps/Instances"):
        os.remove(os.getcwd()+"/Maps/Instances/"+file)
    #for file in os.listdir(CWD+"/Maps/Materials"):
    #    os.remove(CWD+"/Maps/Materials/"+file)
    #for file in os.listdir(os.getcwd()+"/data/Dynamics"):
    #    os.remove(os.getcwd()+"/data/Dynamics/"+file)
    #for file in os.listdir(CWD+"/Maps/Entities"):
    #    os.remove(CWD+"/Maps/Entities/"+file)
    #for file in os.listdir(os.getcwd()+"/data/DynMaterials"):
        #os.remove(os.getcwd()+"/data/DynMaterials/"+file)
    #for file in os.listdir(os.getcwd()+"/data/Textures"):
        #os.remove(os.getcwd()+"/data/Textures/"+file)
    #for file in os.listdir(CWD+"/Maps/Terrain"):
    #    os.remove(CWD+"/Maps/Terrain/"+file)
    #for file in os.listdir(os.getcwd()+"/data/DynInstances"):
        #os.remove(os.getcwd()+"/data/DynInstances/"+file)

def ClearTextures(CWD):
    for file in os.listdir(CWD+"/ExtractedFiles/Textures"):
        if file != "cubemaps":
            os.remove(CWD+"/ExtractedFiles/Textures/"+file)
    for file in os.listdir(CWD+"/ExtractedFiles/Textures/Cubemaps"):
        os.remove(CWD+"/ExtractedFiles/Textures/Cubemaps/"+file)

def ClearAudio(top):
    for File in os.listdir(os.getcwd()+"/out/audio"):
        os.remove(os.getcwd()+"/out/audio/"+File)
    #MainWindow(top)

def GeneratePackageCache(path):
    PackageCache={}
    Packages=os.listdir(path)
    Packages.sort(reverse=True)
    usedIds=[]
    for File in Packages:
        temp=File.split("_")
        FileD=open(path+"/"+File,"rb")
        FileD.seek(0x10)
        PID=int.from_bytes(FileD.read(2),"little")
        FileD.close()
        if PID not in usedIds:
            PackageCache[PID] = File
            usedIds.append(PID)
    return PackageCache
path="E:\SteamLibrary\steamapps\common\Destiny2\packages"
def init():
    global PackageCache,H64Data,Cwd
    PackageCache=GeneratePackageCache(path)
    H64Data=Package.ReadHash64(PackageCache,path)
    Cwd=os.getcwd()

