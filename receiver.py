import os,filelist

#brouillon

def receive_local(dir,dic):
    file_listr = filelist.parcours(dir,dic)
    #recoit la liste de l'envoyeur et crée le generateur