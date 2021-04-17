import os,filelist

#brouillon

def receive_local(dir,dict):
    os.chdir(dir)
    file_listr = filelist.parcours('.',dict)